import os
import json
import psutil
from telegram import Update, ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

members_file = "members.json"

# Load members database
if os.path.exists(members_file):
    with open(members_file, "r") as f:
        members_db = json.load(f)
else:
    members_db = {}

def save_members():
    with open(members_file, "w") as f:
        json.dump(members_db, f)

async def store_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    if not user:
        return

    user_id = str(user.id)
    user_name = user.full_name
    chat_id = str(chat.id)

    if chat.type in ["group", "supergroup"]:
        if chat_id not in members_db:
            members_db[chat_id] = {}
        members_db[chat_id][user_id] = user_name
    elif chat.type == "private":
        if "private_users" not in members_db:
            members_db["private_users"] = {}
        members_db["private_users"][user_id] = user_name

    save_members()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await store_user(update, context)
    await update.message.reply_text("I am Mention Bot.
Add me to your group and send /mentionall")

async def mention_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    members = members_db.get(chat_id, {})

    if not members:
        await update.message.reply_text("No members found.")
        return

    text = ""
    for uid, name in members.items():
        text += f"[{name}](tg://user?id={uid}) "
        if len(text) > 3500:
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            text = ""

    if text:
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    message = " ".join(context.args)
    sent = 0
    failed = 0
    all_users = set()

    for chat_id, users in members_db.items():
        all_users.update(users.keys())

    for uid in all_users:
        try:
            await context.bot.send_message(chat_id=int(uid), text=message)
            sent += 1
        except:
            failed += 1

    await update.message.reply_text(f"✅ Sent: {sent}
❌ Failed: {failed}")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_users = set()
    total_groups = 0
    total_channels = 0

    for chat_id, users in members_db.items():
        if chat_id == "private_users":
            total_users.update(users.keys())
            continue
        total_users.update(users.keys())
        try:
            chat = await context.bot.get_chat(int(chat_id))
            if chat.type in ["group", "supergroup"]:
                total_groups += 1
            elif chat.type == "channel":
                total_channels += 1
        except:
            pass

    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    text = (
        "*Bot Global Status*
"
        f"👤 Users: `{len(total_users)}`
"
        f"👥 Groups: `{total_groups}`
"
        f"📢 Channels: `{total_channels}`
"
        f"🧠 RAM: `{ram.used // (1024**2)} MB / {ram.total // (1024**2)} MB`
"
        f"💾 Disk: `{disk.used // (1024**2)} MB / {disk.total // (1024**2)} MB`"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def group_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    chat_id = str(chat.id)

    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("This command only works in groups.")
        return

    members = members_db.get(chat_id, {})
    await update.message.reply_text(f"👥 Group Members: `{len(members)}`", parse_mode=ParseMode.MARKDOWN)

def main():
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mentionall", mention_all))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("groupstatus", group_status))
    app.add_handler(MessageHandler(filters.ALL, store_user))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()