from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
import os
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Dummy web server for Koyeb health check
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# Command: /mentionall
async def mention_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command only works in groups.")
        return

    members = set()

    try:
        async for message in context.bot.get_chat_history(chat_id=chat.id, limit=100):
            if message.from_user:
                members.add(message.from_user)
    except Exception as e:
        await update.message.reply_text(f"Error fetching messages: {e}")
        return

    if not members:
        await update.message.reply_text("Couldn't find active members to mention.")
        return

    mentions = []
    for user in members:
        name = user.full_name
        mention = f"[{name}](tg://user?id={user.id})"
        mentions.append(mention)

    mention_text = ' '.join(mentions)
    await update.message.reply_text(mention_text, parse_mode=ParseMode.MARKDOWN)

def main():
    threading.Thread(target=run_web).start()  # Start Flask server
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("mentionall", mention_all))
    print("Bot is running...")
    app_bot.run_polling()

if __name__ == "__main__":
    main()
