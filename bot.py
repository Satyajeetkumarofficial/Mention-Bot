import json
import os
import threading
import psutil
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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "I am a Mention Bot.\nAdd me to your group and send /mentionall to mention all known members."
    )

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

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /broadcast Your message here")
        return

    message = " ".join(context.args)
    sent_count = 0
    failed_count = 0

    all_user_ids = set()
    for chat_users in members_db.values():
        all_user_ids.update(chat_users.keys())

    for user_id in all_user_ids:
        try:
            await context.bot.send_message(chat_id=int(user_id), text=message)
            sent_count += 1
        except:
            failed_count += 1

    await update.message.reply_text(f"Broadcast sent to {sent_count} users. Failed: {failed_count}")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_users = set()
    total_groups = 0
    total_channels = 0

    for chat_id, users in members_db.items():
        total_users.update(users.keys())
        if str(chat_id).startswith("-100"):
            total_groups += 1
        elif str(chat_id).startswith("-"):
            total_channels += 1

    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    status_text = (
        "*Bot Status*\n"
        f"Total Users: `{len(total_users)}`\n"
        f"Total Groups: `{total_groups}`\n"
        f"Total Channels: `{total_channels}`\n"
        f"RAM Usage: `{ram.used // (1024 ** 2)} MB / {ram.total // (1024 ** 2)} MB`\n"
        f"Disk Usage: `{disk.used // (1024 ** 2)} MB / {disk.total // (1024 ** 2)} MB`"
    )

    await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)

def main():
    threading.Thread(target=run_web).start()

    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start_command))
    app_bot.add_handler(CommandHandler("mentionall", mention_all))
    app_bot.add_handler(CommandHandler("adduser", add_user))
    app_bot.add_handler(CommandHandler("broadcast", broadcast))
    app_bot.add_handler(CommandHandler("status", status_command))
    app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), store_user))

    print("Bot is running...")
    app_bot.run_polling()

if __name__ == "__main__":
    main()