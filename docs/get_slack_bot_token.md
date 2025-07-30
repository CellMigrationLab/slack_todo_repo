# 🔎 How to get your Slack Bot Token

There are two ways to get your Slack Bot Token:


## Existing Slack App

If you already have a Slack app set up, you can find the Bot User OAuth Token by following these steps, otherwise, you can create a new Slack app as [described below](#create-a-slack-app).

1. Going to your app's settings on the [Slack API Apps page](https://api.slack.com/apps).
2. Navigating to **OAuth & Permissions**.
3. Scrolling down to the **OAuth Tokens for Your Workspace** section.
4. You will see a token starting with `xoxb-`. This is your Bot User OAuth Token.
5. Copy this token and save it securely.


## **Create a Slack App**

If you don't have a Slack app yet, follow these steps to create one and get your Bot User OAuth Token:

### 1.- Go to [Slack API Apps](https://api.slack.com/apps)

### 2.- Click on "Create New App"

### 3.- Choose "From scratch"

### 4.- Give your app a name and select your workspace

### 5.- Click "Create App"

### 6.- Configure Bot Scopes

- Navigate to **OAuth & Permissions** in the left sidebar.
- Under **Scopes**, find **Bot Token Scopes**.
- Add the following scopes:

    ```plaintext
    app_mentions:read
    channels:history
    channels:read
    chat:write
    groups:history
    groups:read
    im:history
    im:read
    mpim:read
    users:read
    ```
### 7.- Find the Bot User OAuth Token
- Scroll down to the **OAuth Tokens for Your Workspace** section.
- You will see a token starting with `xoxb-`. This is your Bot User OAuth Token.
- Copy this token and save it securely.
