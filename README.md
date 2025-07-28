# 🧾 Slack → GitHub To-Do Bot

This bot pulls `@todo <@yourname>` messages from Slack and creates GitHub issues in a private repo.

## ✅ What It Does

- Runs once daily (or manually via GitHub Actions)
- Scans Slack for messages containing `@todo` **and tagging you**
- Converts matches into GitHub Issues with context, link, and display names
- Supports:
  - ✅ Direct messages (DMs)
  - ✅ Public/private channels (only if bot is invited)
  - ✅ Thread replies (uses parent as task)
  - ✅ Slack username rendering (no raw user IDs)

---

## 🚀 Setup Instructions

### 1. **Create a Private GitHub Repo Using This Template**

- Clone or fork this project into a new private repo.

---

### 2. **Set the Following GitHub Secrets**  
_Go to: Settings → Secrets → Actions → New repository secret_

| Name               | Example Value         | Description                           |
|--------------------|-----------------------|---------------------------------------|
| `SLACK_BOT_TOKEN`  | `xoxb-...`            | Your Slack Bot OAuth token            |
| `SLACK_USERNAME`   | `U01ABCXYZ99`         | Your Slack **user ID** (not handle)   |
| `GITHUB_TOKEN`     | (auto-generated)      | GitHub’s default token (read/write)   |

🔎 To get your Slack user ID:  
Click your profile in Slack → “Profile” → “More” → “Copy member ID”

---

### 3. **Create & Configure a Slack App**

Go to: https://api.slack.com/apps → “Create New App”

1. **Bot Scopes** (OAuth & Permissions):
    ```
app_mentions:read
channels:history
channels:read
chat:write
groups:history
groups:read
im:history
im:read
mpim:read
    ```

2. **Install App to Workspace**

3. **Invite Bot to Any Relevant Channels**:
    ```
    /invite @your-bot-name
    ```

---

### 4. **Enable GitHub Actions**

- GitHub Action runs:
  - 📅 Automatically once daily (e.g. 8am weekdays)
  - 👆 Or manually via the Actions tab → "Run workflow"

---

## ✅ Example Usage

In Slack:

```text
@todo <@U01ABCXYZ99> Follow up on antibody order
```

➡️ GitHub Issue will be created:

```
**Location:** Direct Message
**From Slack:** https://yourworkspace.slack.com/archives/DM123/p123456

**Context:**
Follow up on antibody order
```

---

## 📎 Notes & Best Practices

- Mentions must use `<@SlackUserID>` format — tagging via autocomplete does this by default.
- The bot **only reads channels it's a member of**
- Mentions in **DMs or thread replies** are fully supported
- Usernames are rendered in plain text in GitHub (e.g. `@Guillaume Jacquemet`)
- API usage is rate-limited for safety

---

## 🧠 Manual GitHub Tasks

You can also create issues manually — they won’t be overwritten or removed by the bot.

---

## 🛟 Troubleshooting

- ❌ **Issue not created?**
  - Make sure you're tagging your Slack user ID
  - Check if the bot is invited to the channel
  - Verify scopes and token permissions
- 🛑 **403 GitHub error?**
  - Ensure GitHub Actions is set to “Read and write” permission under repo → Settings → Actions → General

---

MIT © Jacquemet Lab
