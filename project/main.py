import asyncio
from pyrogram import Client
from database.db import get_db
from core.publisher import publisher
from core.retargeting import retarget
from handlers.chat import register as chat_register
from handlers.admin import register as admin_register
import config

bot = Client("bot", config.API_ID, config.API_HASH, bot_token=config.BOT_TOKEN)
userbot = Client("user", config.API_ID, config.API_HASH)

async def main():
    db, cur = get_db()

    chat_register(bot, cur)
    admin_register(bot, cur)

    await bot.start()
    await userbot.start()

    asyncio.create_task(publisher(userbot, cur))
    asyncio.create_task(retarget(bot, cur))

    await asyncio.Event().wait()

asyncio.run(main())