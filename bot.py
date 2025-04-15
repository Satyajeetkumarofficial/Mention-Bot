from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
import os
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Flask app for health check
app = Flask(__name__)

@app.route("/")
def index():
    return "Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# Telegram bot logic
async def mention_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command only works in groups.")
        return

    try:
        admins = await context.bot.get_chat_administrators(chat.id)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        return

    mentions = [f"[{a.user.full_name}](tg://user?id={a.user.id})" for a in admins]
    await update.message.reply_text(" ".join(mentions), parse_mode=ParseMode.MARKDOWN)

def main():
    threading.Thread(target=run_web).start()  # Start Flask server
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("mentionall", mention_all))
    print("Bot is running...")
    app_bot.run_polling()

if __name__ == "__main__":
    main()
