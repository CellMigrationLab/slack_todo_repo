# 🧾 Slack → GitHub To-Do Bot

This bot pulls `@todo <@yourname>` messages from Slack and creates GitHub issues in a private repo.

## ✅ What It Does

- Runs once daily (or manually via [GitHub Actions](.github/workflows/slack_todo.yml))
- Scans Slack for messages containing `@todo` **and tagging you**
- Converts matches into GitHub Issues with context, link, and display names
- Supports:
  - ✅ Direct messages (DMs)
  - ✅ Public/private channels (only if bot is invited)
  - ✅ Thread replies (uses parent as task)
  - ✅ Slack username rendering (no raw user IDs)
  - ✅ GitHub labels via inline Slack tags

---

## 🚀 Setup Instructions

### 1. **Create a Private GitHub Repo Using This Template**

- Clone or fork this project into a new private repo:  <button name="button" onclick="https://github.com/new?template_name=slack_todo_repo&template_owner=CellMigrationLab">Clone</button> 


### 2. **Set the Following GitHub Secrets**  
**In your repository, go to:** _Settings → Secrets → Actions → New repository secret_

| Name               | Example Value         | Description                           | How to Get It                      |
|--------------------|-----------------------|---------------------------------------|-------------------------------------|
| `SLACK_BOT_TOKEN`  | `xoxb-...`            | Your Slack Bot OAuth token            |          [Link here](docs/get_slack_bot_token.md)                 |
| `SLACK_USERNAME`   | `U01ABCXYZ99`         | Your Slack **user ID** (not handle)   |          [Link here](docs/get_slack_id.md)                 |
| `GITHUB_TOKEN`     | (auto-generated)      | GitHub’s default token (read/write)   |      [Link here](docs/create_github_token.md)                 |

### 3. **Install the Slack App on Your Workspace**

- Go to [Slack API Apps](https://api.slack.com/apps)
- Click on your app or create a new one as described in [this guide](docs/get_slack_bot_token.md) 
- Click **Install App to Workspace** and authorize it
- Invite the bot to any channels you want it to monitor (e.g. `#general`, `#random`)
- Make sure the bot is a member of any channels you want to monitor
- If you want to use the bot in DMs, it must be added to those conversations



### 4. **Enable GitHub Actions**

- GitHub Action runs:
  - 📅 Automatically once daily (e.g. 8am weekdays)
  - 👆 Or manually via the Actions tab → "Run workflow"
- Be sure to enable GitHub Actions in your repo settings:
  - Go to **Settings → Actions → General**
  - Set **Workflow permissions** to "Read and write permissions"
  - Enable "Allow GitHub Actions to create and approve pull requests"
## ✅ Example Usage

➡️ Message in Slack:

```text
@todo <@U01ABCXYZ99> Follow up on antibody order #urgent #project(pacsin2)
```

⚙️ GitHub Issue will be created:

```markdown
**Location:** Direct Message  
**From Slack:** https://yourworkspace.slack.com/archives/DM123/p123456

**Context:**
Follow up on antibody order
```

And labeled with:
```markdown
**Labels:** urgent, project:pacsin2
```

---

## 🏷️ Label Syntax

- Use hashtags in Slack to assign GitHub labels:
  - `#urgent` → becomes `urgent`
  - `#project(pacsin2)` → becomes `project:pacsin2`
- Labels are automatically added to issues
- Duplicates are skipped (including previously closed issues)

---

## 📎 Notes & Best Practices

- Mentions must use `<@SlackUserID>` format — tagging via autocomplete does this by default.
- The bot **only reads channels it's a member of**
- Mentions in **DMs or thread replies** are fully supported
- Usernames are rendered in plain text in GitHub (e.g. `@Guillaume Jacquemet`)
- API usage is rate-limited for safety
- Forwarded emails must include `@todo` and a tag

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
