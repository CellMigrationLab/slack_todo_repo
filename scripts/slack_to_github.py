import os
import re
import requests
from datetime import datetime, timedelta
from slack_sdk import WebClient

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_USERNAME = os.environ["SLACK_USERNAME"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPO = os.environ["GITHUB_REPOSITORY"]

client = WebClient(token=SLACK_BOT_TOKEN)

def fetch_mentions():
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    oldest = int(yesterday.timestamp())
    channels = client.conversations_list(types="public_channel,private_channel")["channels"]

    for channel in channels:
        cid = channel["id"]
        try:
            messages = client.conversations_history(channel=cid, oldest=oldest)["messages"]
            for msg in messages:
                if f"@{SLACK_USERNAME}" in msg.get("text", "") and "@todo" in msg.get("text", ""):
                    yield msg, cid
        except Exception:
            continue

def get_permalink(channel, ts):
    return client.chat_getPermalink(channel=channel, message_ts=ts)["permalink"]

def fetch_parent_message(channel, thread_ts):
    try:
        replies = client.conversations_replies(channel=channel, ts=thread_ts)["messages"]
        return replies[0]["text"] if replies else ""
    except Exception:
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

for message, channel in fetch_mentions():
    text = message.get("text", "").strip()
    ts = message.get("ts")
    thread_ts = message.get("thread_ts", ts)
    permalink = get_permalink(channel, ts)
    context = fetch_parent_message(channel, thread_ts) if thread_ts != ts else text
    title = context[:60] + ("..." if len(context) > 60 else "")
    body = f"**From Slack:** {permalink}

**Context:**
{context}"
    create_github_issue(title, body)
