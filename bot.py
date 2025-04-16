
import logging
from pymongo import MongoClient
from telegram import Update
from telegram.constants import ChatType
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ChatMemberHandler
)

# --- Configuration ---
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))
YOUR_ADMIN_USER_ID = int(os.getenv("YOUR_ADMIN_USER_ID", "0"))

# MongoDB Setup
client = MongoClient(MONGO_URL)
db = client["mention_bot"]
users_collection = db["users"]
groups_collection = db["groups"]

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Commands

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm a mention bot.\nType /help to see available commands.")
    if update.effective_chat.type == ChatType.PRIVATE:
        users_collection.update_one(
            {"user_id": update.effective_user.id},
            {"$set": {"username": update.effective_user.username}},
            upsert=True
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Start the bot\n"
        "/help - Show help\n"
        "/mentionall - Mention all group members\n"
        "/broadcast - Broadcast to all users (admin only)\n"
        "/status - Bot stats"
    )

async def mentionall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await update.message.reply_text("Use this command in a group.")

    members = users_collection.find({"chat_id": update.effective_chat.id})
    mention_text = ""
    count = 0

    for user in members:
        user_id = user["user_id"]
        mention_text += f"[‎](tg://user?id={user_id})"
        count += 1
        if count % 5 == 0:
            await update.message.reply_text(mention_text)
            mention_text = ""

    if mention_text:
        await update.message.reply_text(mention_text)

async def chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.chat_member
    user = member.new_chat_member.user

    if member.new_chat_member.status in ["member", "administrator"]:
        users_collection.update_one(
            {"user_id": user.id, "chat_id": update.effective_chat.id},
            {"$set": {
                "username": user.username,
                "chat_id": update.effective_chat.id
            }},
            upsert=True
        )
        groups_collection.update_one(
            {"chat_id": update.effective_chat.id},
            {"$set": {"title": update.effective_chat.title}},
            upsert=True
        )
        if LOG_CHANNEL_ID != 0:
            await context.bot.send_message(
                chat_id=LOG_CHANNEL_ID,
                text=f"{user.first_name} joined {update.effective_chat.title}"
            )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != ChatType.PRIVATE:
        return await update.message.reply_text("Use in private chat.")
    if update.effective_user.id != YOUR_ADMIN_USER_ID:
        return await update.message.reply_text("You are not authorized.")
    if not context.args:
        return await update.message.reply_text("Usage: /broadcast Your message here")

    msg = " ".join(context.args)
    count = 0
    for user in users_collection.find():
        try:
            await context.bot.send_message(chat_id=user["user_id"], text=msg)
            count += 1
        except:
            continue

    await update.message.reply_text(f"Broadcast sent to {count} users.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_users = users_collection.count_documents({})
    total_groups = groups_collection.count_documents({})
    await update.message.reply_text(
        f"Bot Status:\nUsers: {total_users}\nGroups: {total_groups}"
    )

# Main Runner

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mentionall", mentionall))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(ChatMemberHandler(chat_member, ChatMemberHandler.CHAT_MEMBER))

    print("Bot running...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
