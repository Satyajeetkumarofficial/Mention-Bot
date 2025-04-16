
# Telegram Mention Bot

A powerful Telegram bot built in Python that can:

- Welcome users with /start
- Mention all group members (old and new) with /mentionall
- Broadcast messages to all users
- Show bot status (total users and groups)
- Log user joins to a log channel
- Store users and groups using MongoDB
- Easily deployable on [Koyeb](https://www.koyeb.com)

## Features

- /start – Sends welcome message
- /help – Lists available commands
- /mentionall – Mentions all group members (stored in DB)
- /broadcast <text> – Sends a message to all users (admin only)
- /status – Shows total users and groups
- MongoDB integration to track users and groups
- Logs member joins to a specific log channel

## Environment Variables

Set these in your Koyeb dashboard:

| Variable              | Description                            |
|-----------------------|----------------------------------------|
| BOT_TOKEN             | Your Telegram Bot Token                |
| MONGO_URL             | Your MongoDB connection string         |
| LOG_CHANNEL_ID        | Log channel ID (e.g. -1001234567890)   |
| YOUR_ADMIN_USER_ID    | Your Telegram numeric user ID          |

## Deployment (Koyeb)

1. Push this repo to GitHub
2. Go to Koyeb and create a new service
3. Link your GitHub repo
4. Set environment variables
5. Set run command: `python bot.py`
6. Deploy!

## Files

- bot.py – Main bot code
- requirements.txt – Dependencies
- Procfile – For Koyeb process

## License

MIT License
