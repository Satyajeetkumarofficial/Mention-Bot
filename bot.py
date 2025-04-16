
from pyrogram import Client, filters
from pyrogram.types import Message

app = Client("mention_bot", bot_token="YOUR_BOT_TOKEN", api_id=123456, api_hash="YOUR_API_HASH")

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text("I am Mention Bot. Add me to your group and send /mentionall")

app.run()
