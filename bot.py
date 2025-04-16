import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pymongo import MongoClient
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configs
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
MONGO_URL = os.environ.get("MONGO_URL", "YOUR_MONGO_URL")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001234567890"))

# MongoDB setup
client = MongoClient(MONGO_URL)
db = client["telegram_bot"]
users_collection = db["users"]
groups_collection = db["groups"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {user.first_name}, welcome to the Mention Bot!"
    )
    users_collection.update_one(
        {"user_id": user.id},
        {"$set": {"username": user.username}},
        upsert=True
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/mentionall - Mention all group members\n"
        "/broadcast <message> - Send message to all users\n"
        "/status - Show total users and groups"
    )

async def mention_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ['group', 'supergroup']:
        return await update.message.reply_text("Use this in groups only.")

    members = users_collection.find()
    mentions = [f"[{m.get('username') or 'user'}](tg://user?id={m['user_id']})" for m in members]

    msg = ' '.join(mentions)
    await update.message.reply_text(msg, parse_mode="Markdown")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != update.effective_chat.get_member(update.effective_user.id).user.id:
        return

    if not context.args:
        return await update.message.reply_text("Please provide a message to broadcast.")

    message = ' '.join(context.args)
    for user in users_collection.find():
        try:
            await context.bot.send_message(chat_id=user['user_id'], text=message)
        except Exception as e:
            logger.error(f"Error sending message to {user['user_id']}: {e}")

    await update.message.reply_text("Broadcast sent.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_users = users_collection.count_documents({})
    total_groups = groups_collection.count_documents({})
    await update.message.reply_text(f"Total Users: {total_users}\nTotal Groups: {total_groups}")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mentionall", mention_all))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("status", status))

    logger.info("Bot started...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
