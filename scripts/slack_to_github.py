import os
import re
import time
import requests
from datetime import datetime, timedelta
from slack_sdk import WebClient

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_USERNAME = os.environ["SLACK_USERNAME"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPO = os.environ["GITHUB_REPOSITORY"]

client = WebClient(token=SLACK_BOT_TOKEN)
user_cache = {}

def extract_tags(text):
    tags = re.findall(r"#([a-zA-Z0-9_-]+)(\(([^)]+)\))?", text)
    labels = []
    for tag, _, val in tags:
        if val:
            labels.append(f"{tag.lower()}: {val.lower()}")
        else:
            labels.append(tag.lower())
    return labels


def extract_task_title(text):
    # Remove @todo and @username
    text = re.sub(r"@todo", "", text, flags=re.IGNORECASE)
    text = re.sub(rf"<@{SLACK_USERNAME}>", "", text, flags=re.IGNORECASE)
    # Remove tags
    text = re.sub(r"#\w+(\([^)]+\))?", "", text)
    return text.strip().split("\n")[0][:80]

def extract_message_text(msg):
    """Extracts meaningful text even from forwarded emails or Slack 'blocks'."""
    if "text" in msg and msg["text"]:
        return msg["text"]

    # fallback: check for blocks with text
    if "blocks" in msg:
        for block in msg["blocks"]:
            if block.get("type") == "section":
                if "text" in block and block["text"].get("type") == "mrkdwn":
                    return block["text"].get("text", "")

    # fallback: check for attachments
    if "attachments" in msg:
        for att in msg["attachments"]:
            if "text" in att:
                return att["text"]
            if "fallback" in att:
                return att["fallback"]

    return ""



def resolve_user_name(user_id):
    if user_id in user_cache:
        return user_cache[user_id]
    try:
        user_info = client.users_info(user=user_id)
        real_name = user_info["user"]["real_name"]
        user_cache[user_id] = real_name
        return real_name
    except:
        return user_id

def replace_user_ids_with_names(text):
    user_ids = re.findall(r"<@([A-Z0-9]+)>", text)
    for uid in user_ids:
        name = resolve_user_name(uid)
        text = text.replace(f"<@{uid}>", f"@{name}")
    return text

def list_all_channels():
    cursor = None
    while True:
        resp = client.conversations_list(
            types="public_channel,private_channel",
            limit=100,
            cursor=cursor
        )
        for channel in resp["channels"]:
            yield channel
        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

def fetch_full_thread(channel, thread_ts):
    try:
        replies = client.conversations_replies(channel=channel, ts=thread_ts)["messages"]
        formatted = []
        for msg in replies:
            author = resolve_user_name(msg.get("user", ""))
            text = replace_user_ids_with_names(msg.get("text", ""))
            formatted.append(f"**{author}:** {text}")
        return "\n\n".join(formatted)
    except:
        return "Thread could not be retrieved."

def fetch_mentions():
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    oldest = int(yesterday.timestamp())

    # 1. Public and Private Channels
    for channel in list_all_channels():
        cid = channel["id"]
        cname = channel.get("name", "unknown")

        if not channel.get("is_member"):
            print(f"Skipping channel: {cname} (not a member)")
            continue

        print(f"Checking channel: {cname} ({cid})")
        try:
            messages = client.conversations_history(channel=cid, oldest=oldest)["messages"]
            for msg in messages:
                text = extract_message_text(msg)
                if "@todo" in text and f"<@{SLACK_USERNAME}>" in text:
                    print(f"--> MATCHED (channel): {text}")
                    yield msg, cid, cname

                if msg.get("reply_count", 0) > 0:
                    replies = client.conversations_replies(channel=cid, ts=msg["ts"])["messages"][1:]
                    for reply in replies:
                        rtext = reply.get("text", "")
                        if "@todo" in rtext and f"<@{SLACK_USERNAME}>" in rtext:
                            print(f"--> MATCHED (thread reply): {rtext}")
                            yield reply, cid, cname
            time.sleep(1)
        except Exception as e:
            print(f"Error reading channel {cname}: {e}")
            time.sleep(2)

    # 2. Direct Messages (IMs)
    ims = client.conversations_list(types="im")["channels"]
    for im in ims:
        cid = im["id"]
        print(f"Checking DM channel: {cid}")
        try:
            messages = client.conversations_history(channel=cid, oldest=oldest)["messages"]
            for msg in messages:
                text = msg.get("text", "")
                if "@todo" in text and f"<@{SLACK_USERNAME}>" in text:
                    print(f"--> MATCHED (DM): {text}")
                    yield msg, cid, "Direct Message"
            time.sleep(1)
        except Exception as e:
            print(f"Error reading DM {cid}: {e}")
            time.sleep(2)

def get_permalink(channel, ts):
    try:
        return client.chat_getPermalink(channel=channel, message_ts=ts)["permalink"]
    except:
        return "Permalink not available"

def issue_already_exists(permalink):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    params = { "state": "all", "per_page": 100 }  # <-- check all issues, not just open
    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        print("Failed to fetch issues:", res.text)
        return False
    issues = res.json()
    for issue in issues:
        if permalink in issue.get("body", ""):
            return True
    return False


def create_github_issue(title, body, labels):
    permalink_line = body.splitlines()[1].strip() if len(body.splitlines()) > 1 else ""
    if issue_already_exists(permalink_line):
        print("Skipped: Issue already exists for this Slack message.")
        return
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    data = { "title": title, "body": body, "labels": labels }
    res = requests.post(url, headers=headers, json=data)
    if res.status_code != 201:
        print("GitHub issue creation failed:", res.text)
    else:
        print(f"✅ Created GitHub issue: {title} with labels {labels}")


# 🔁 Run full extraction
for message, channel, location in fetch_mentions():
    text = message.get("text", "").strip()
    ts = message.get("ts")
    thread_ts = message.get("thread_ts", ts)
    permalink = get_permalink(channel, ts)
    context = fetch_full_thread(channel, thread_ts) if thread_ts != ts else replace_user_ids_with_names(text)
    title = extract_task_title(text)
    labels = extract_tags(text)
    body = f"**Location:** {location}\n**From Slack:** {permalink}\n\n**Context:**\n{context}"
    create_github_issue(title, body, labels)
