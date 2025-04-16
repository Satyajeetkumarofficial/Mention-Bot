import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from pymongo import MongoClient
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

mongo = MongoClient(MONGO_URL)
db = mongo["mentionbot"]
users_col = db["users"]

app = Client("mention_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.private & filters.command("start"))
async def start(client, message: Message):
    user_id = message.from_user.id
    users_col.update_one({"_id": user_id}, {"$set": {"name": message.from_user.first_name}}, upsert=True)
    await message.reply_text(f"Hey {message.from_user.first_name}, I'm your group mention bot!")

@app.on_message(filters.command("mentionall") & filters.group)
async def mention_all(client: Client, message: Message):
    try:
        # Check if user is admin or group owner
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await message.reply("❌ केवल ग्रुप एडमिन्स इस कमांड का उपयोग कर सकते हैं।")

        # Extract custom message after command, if any
        custom_message = message.text.split(" ", 1)
        if len(custom_message) > 1:
            custom_text = custom_message[1]
        else:
            custom_text = ""

        mentions = []
        async for m in client.get_chat_members(message.chat.id):
            if not m.user.is_bot:
                mentions.append(f"[{m.user.first_name}](tg://user?id={m.user.id})")

        mention_text = ''
        count = 0
        for mention in mentions:
            mention_text += mention + " "
            count += 1
            if count % 5 == 0:
                if custom_text:
                    await message.reply(mention_text + "\n\n" + custom_text)
                else:
                    await message.reply(mention_text)
                mention_text = ''
        if mention_text:
            if custom_text:
                await message.reply(mention_text + "\n\n" + custom_text)
            else:
                await message.reply(mention_text)

    except Exception as e:
        print("Error:", e)
        await message.reply("⚠️ कुछ गलत हो गया।")
@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to a message to broadcast.")
    
    sent = 0
    for user in users_col.find():
        try:
            await client.copy_message(user["_id"], message.chat.id, message.reply_to_message.message_id)
            sent += 1
            await asyncio.sleep(0.1)
        except:
            continue
    await message.reply(f"Broadcast sent to {sent} users.")

@app.on_message(filters.command("status") & filters.user(ADMIN_ID))
async def status(client, message: Message):
    total_users = users_col.count_documents({})
    groups = users_col.distinct("group_id")
    await message.reply_text(f"Bot Status:\nTotal Users: {total_users}\nTotal Groups: {len(groups)}")

@app.on_message(filters.group)
async def save_group_user(client, message: Message):
    user = message.from_user
    if user and not user.is_bot:
        users_col.update_one(
            {"_id": user.id},
            {"$set": {"name": user.first_name, "group_id": message.chat.id}},
            upsert=True
        )

def run_dummy_server():
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is running!")

    server = HTTPServer(('0.0.0.0', 8080), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server).start()
app.run()
