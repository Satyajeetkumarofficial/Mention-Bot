# Telegram Mention Bot

A Telegram bot to mention all members (including past ones), broadcast messages, and show bot/group stats.

## Features

- Mention all users in a group using `/mentionall`
- Broadcast messages to all users using `/broadcast`
- Show bot-wide stats with `/status`
- Show group-specific user count with `/groupstatus`

## Deployment

1. Clone the repo or extract this ZIP.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your bot token in an environment variable:
   ```bash
   export BOT_TOKEN=your_bot_token_here
   ```
4. Run the bot:
   ```bash
   python bot.py
   ```

## Notes

- Users must start the bot in private chat to receive broadcast messages.
- The bot stores all users who interact in groups or private chat.