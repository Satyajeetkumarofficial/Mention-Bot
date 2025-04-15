from telegram import Update, ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = '7750870847:AAGBCFv5I4-aeYj1T2mWK5y0Z-t-PfoT7wk'  # <-- Replace with your token

# This command will mention all admins
async def mention_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command only works in group chats.")
        return

    try:
        admins = await context.bot.get_chat_administrators(chat.id)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        return

    mentions = []
    for admin in admins:
        user = admin.user
        name = user.full_name
        mention = f"[{name}](tg://user?id={user.id})"
        mentions.append(mention)

    mention_text = ' '.join(mentions)
    await update.message.reply_text(mention_text, parse_mode=ParseMode.MARKDOWN)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("mentionall", mention_all))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
