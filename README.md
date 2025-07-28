# 🧾 Slack → GitHub To-Do Bot

This bot pulls `@todo @<yourname>` messages from Slack and creates GitHub issues.

## ✅ What It Does

- Runs once daily (8am weekdays) or manually
- Scans Slack messages where you're tagged with `@todo`
- Converts those into GitHub Issues

## 🚀 Setup

1. **Create a private GitHub repo using this template**

2. **Add 3 secrets (Settings > Secrets > Actions):**

| Name              | Example Value        | Purpose                    |
|-------------------|----------------------|----------------------------|
| `SLACK_BOT_TOKEN` | `xoxb-...`           | From your Slack App        |
| `SLACK_USERNAME`  | `guillaume`          | Your Slack handle (no @)   |
| `GITHUB_TOKEN`    | (auto-generated)     | Provided by GitHub Actions |

3. **Create a Slack App:**

- Go to https://api.slack.com/apps → "Create New App"
- Add bot token scopes:
  - `channels:history`, `groups:history`, `chat:write`, `app_mentions:read`
- Install the app to your workspace
- Invite it to the channels you want to monitor

4. **Enable the GitHub Action**

- It'll run daily or can be manually triggered in the Actions tab

## 🧠 Manual Tasks

You can also create issues directly in GitHub — they won't be affected.

## 📎 Notes

- Thread replies are supported — the parent message is used as task context.
- You must be mentioned with `@todo @yourusername` to trigger an issue.
