
from pyrogram import Client, filters
from aiohttp import web
import asyncio

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("mention_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("I am Mention Bot.\nAdd me to your group and send /mentionall")

# Dummy HTTP server for health check
async def hello(request):
    return web.Response(text="Bot is running!")

async def start_server():
    app_web = web.Application()
    app_web.router.add_get("/", hello)
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

loop = asyncio.get_event_loop()
loop.create_task(start_server())

app.run()
