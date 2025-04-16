import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from pymongo import MongoClient
import asyncio
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

bot = Client("mention-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

mongo = MongoClient(MONGO_URL)
db = mongo["mention_bot"]
users_collection = db["group_users"]

@bot.on_message(filters.group & filters.new_chat_members)
async def save_new_members(client, message):
    for user in message.new_chat_members:
        if not user.is_bot:
            users_collection.update_one(
                {"user_id": user.id, "chat_id": message.chat.id},
                {"$set": {
                    "user_id": user.id,
                    "first_name": user.first_name,
                    "chat_id": message.chat.id
                }},
                upsert=True
            )

@bot.on_message(filters.command("mentionall") & filters.group)
async def mention_all(client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await message.reply("❌ केवल ग्रुप एडमिन्स इस कमांड का उपयोग कर सकते हैं।")

    custom_msg = message.text.split(" ", 1)
    custom_text = custom_msg[1] if len(custom_msg) > 1 else ""

    users = users_collection.find({"chat_id": message.chat.id})
    mentions = [f"[{user['first_name']}](tg://user?id={user['user_id']})" for user in users]

    mention_text = ""
    count = 0
    for mention in mentions:
        mention_text += mention + " "
        count += 1
        if count % 50 == 0:
            await message.reply(mention_text + (f"\n\n{custom_text}" if custom_text else ""))
            mention_text = ""
            await asyncio.sleep(2)

    if mention_text:
        await message.reply(mention_text + (f"\n\n{custom_text}" if custom_text else ""))

print("Bot is running...")
def run_dummy_server():
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is running!")

    server = HTTPServer(('0.0.0.0', 8080), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server).start()
bot.run()
