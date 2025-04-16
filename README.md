# Telegram Mention Bot

A Telegram bot built with Python to:
- Mention all group members (including previously joined ones)
- Broadcast messages to all users
- Show bot status (user count, RAM, storage, etc.)
- Webhook compatibility for platforms like Koyeb

---

## Features

- `/start` — Introduction message
- `/mentionall` — Mentions all users in a group
- `/adduser <user_id> <full name>` — Manually add user if not tracked
- `/broadcast <message>` — Send message to all saved users
- `/status` — Shows number of users, groups, RAM & disk usage

---

## Deployment (Koyeb or similar)

### 1. **Clone or Upload Project**
Upload all files including:
- `bot.py`
- `requirements.txt`
- `members.json` (optional, auto-created)
- `README.md`

### 2. **Create Python App**
Use a service like [Koyeb](https://www.koyeb.com) or [Render](https://render.com):

- Set **Build & Run** command to:
  ```bash
  pip install -r requirements.txt && python bot.py
