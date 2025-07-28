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

def fetch_mentions():
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    oldest = int(yesterday.timestamp())

    # 1. Channels (public/private)
    channels = client.conversations_list(types="public_channel,private_channel")["channels"]
    for channel in channels:
        cid = channel["id"]
        cname = channel.get("name", "unknown")

        if not channel.get("is_member"):
            print(f"Skipping channel: {cname} (not a member)")
            continue

        print(f"Checking channel: {cname} ({cid})")
        try:
            messages = client.conversations_history(channel=cid, oldest=oldest)["messages"]
            for msg in messages:
                text = msg.get("text", "")
                if "@todo" in text and f"<@{SLACK_USERNAME}>" in text:
                    print(f"--> MATCHED (channel): {text}")
                    yield msg, cid, cname
            time.sleep(1)
        except Exception as e:
            print(f"Error reading channel {cname}: {e}")
            time.sleep(2)

    # 2. Direct messages (IMs)
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

def fetch_parent_message(channel, thread_ts):
    try:
        replies = client.conversations_replies(channel=channel, ts=thread_ts)["messages"]
        return replies[0]["text"] if replies else ""
    except:
        return ""

def create_github_issue(title, body):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    data = { "title": title, "body": body }
    res = requests.post(url, headers=headers, json=data)
    if res.status_code != 201:
        print("GitHub issue creation failed:", res.text)

for message, channel, location in fetch_mentions():
    text = message.get("text", "").strip()
    ts = message.get("ts")
    thread_ts = message.get("thread_ts", ts)
    permalink = get_permalink(channel, ts)
    raw_context = fetch_parent_message(channel, thread_ts) if thread_ts != ts else text
    context = replace_user_ids_with_names(raw_context)
    title = context[:60] + ("..." if len(context) > 60 else "")
    body = f"**Location:** {location}\n**From Slack:** {permalink}\n\n**Context:**\n{context}"
    create_github_issue(title, body)
