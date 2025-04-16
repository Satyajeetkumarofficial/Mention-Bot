import logging
import asyncio
import os
from telegram.ext import Application, CommandHandler
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = AsyncIOMotorClient(MONGO_URL)
db = client["mention_bot"]
users_collection = db["users"]

async def start(update, context):
    await update.message.reply_text("Hello! I'm alive.")

async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    logger.info("Bot started...")
    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    asyncio.get_event_loop().run_until_complete(main())
