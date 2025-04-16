
import os
import json
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import asyncio
import psutil

API_ID = int(os.getenv("API_ID", 123456))
API_HASH = os.getenv("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")

app = Client("mention_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DB_FILE = "users.json"

def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f)

@app.on_message(filters.private & filters.command("start"))
async def start(client, message: Message):
    users = load_users()
    users[str(message.from_user.id)] = message.from_user.first_name
    save_users(users)
    await message.reply_text("I am Mention Bot. Add me to your group and send /mentionall")

@app.on_message(filters.group & filters.command("mentionall"))
async def mention_all(client, message: Message):
    users = []
    async for member in client.get_chat_members(message.chat.id):
        try:
            if not member.user.is_bot:
                users.append(f"[{member.user.first_name}](tg://user?id={member.user.id})")
        except:
            continue

    text = ""
    for i, user in enumerate(users, 1):
        text += user + " "
        if i % 5 == 0:
            await message.reply(text, disable_web_page_preview=True)
            text = ""
            await asyncio.sleep(2)

    if text:
        await message.reply(text, disable_web_page_preview=True)

@app.on_message(filters.private & filters.command("broadcast"))
async def broadcast(client, message: Message):
    if message.from_user.id != YOUR_ADMIN_ID:  # replace with your Telegram user ID
        return await message.reply("You are not authorized.")
    
    text = message.text.split(" ", 1)
    if len(text) < 2:
        return await message.reply("Please send a message to broadcast like: /broadcast YourMessage")
    
    users = load_users()
    success = 0
    for user_id in users:
        try:
            await client.send_message(int(user_id), text[1])
            success += 1
            await asyncio.sleep(0.5)
        except:
            continue
    await message.reply(f"Broadcast sent to {success} users.")

@app.on_message(filters.private & filters.command("status"))
async def status(client, message: Message):
    users = load_users()
    group_count = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ("group", "supergroup"):
            group_count += 1
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    await message.reply_text(f"Users: {len(users)}\nGroups: {group_count}\nCPU: {cpu}%\nRAM: {ram}%")

app.run()
