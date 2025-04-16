import json
import os
import threading
from flask import Flask
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "members.json"

app = Flask(__name__)

# Load or create member list
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        members_db = json.load(f)
else:
    members_db = {}

@app.route("/")
def home():
    return "Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def save_members():
    with open(DATA_FILE, "w") as f:
        json.dump(members_db, f)

# /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "I am a Mention Bot.\nAdd me to your group and send /mentionall to mention all known members."
    )

# Store users when they send a message
async def store_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    if not user or chat.type not in ["group", "supergroup"]:
        return

    chat_id = str(chat.id)
    if chat_id not in members_db:
        members_db[chat_id] = {}
    members_db[chat_id][str(user.id)] = user.full_name
    save_members()

# Add user manually
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /adduser <user_id> <full name>")
        return

    user_id = context.args[0]
    full_name = " ".join(context.args[1:])
    
    if chat_id not in members_db:
        members_db[chat_id] = {}

    members_db[chat_id][user_id] = full_name
    save_members()
    await update.message.reply_text(f"Added: {full_name} (ID: {user_id})")

# Mention all known users
async def mention_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if chat_id not in members_db or not members_db[chat_id]:
        await update.message.reply_text("No members to mention.")
        return

    mentions = []
    for user_id, name in members_db[chat_id].items():
        mention = f"[{name}](tg://user?id={user_id})"
        mentions.append(mention)

    chunk_size = 10
    for i in range(0, len(mentions), chunk_size):
        await update.message.reply_text(
            ' '.join(mentions[i:i + chunk_size]),
            parse_mode=ParseMode.MARKDOWN
        )

def main():
    threading.Thread(target=run_web).start()

    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start_command))
    app_bot.add_handler(CommandHandler("mentionall", mention_all))
    app_bot.add_handler(CommandHandler("adduser", add_user))
    app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), store_user))

    print("Bot is running...")
    app_bot.run_polling()

if __name__ == "__main__":
    main()
