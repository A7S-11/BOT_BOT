import asyncio
import logging
from pyrogram import Client
from database.db import get_db
from core.publisher import publisher
from core.retargeting import retarget
from handlers.chat import register as chat_register
from handlers.admin import register as admin_register
import config

# ───── Logging ─────
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ───── تحقق من الإعدادات ─────
if not config.API_ID or not config.API_HASH or not config.BOT_TOKEN:
    raise ValueError("❌ تأكد من API_ID / API_HASH / BOT_TOKEN")

# ───── Clients ─────
bot = Client("bot", config.API_ID, config.API_HASH, bot_token=config.BOT_TOKEN)
userbot = Client("user", config.API_ID, config.API_HASH)

# ───── Main ─────
async def main():
    db, cur = get_db()

    # ✅ تسجيل الهاندلرز (مصَحَّح)
    chat_register(bot, cur)
    admin_register(bot, db, cur, config.ADMIN_ID)

    # تشغيل
    await bot.start()
    await userbot.start()

    log.info("🤖 Bot Started")

    # مهام آمنة
    async def safe_task(coro_func, name):
        while True:
            try:
                await coro_func()
            except Exception as e:
                log.error(f"❌ Error in {name}: {e}")
                await asyncio.sleep(5)

    asyncio.create_task(safe_task(lambda: publisher(userbot, cur), "publisher"))
    asyncio.create_task(safe_task(lambda: retarget(bot, cur), "retarget"))

    await asyncio.Event().wait()

# ───── Run ─────
if __name__ == "__main__":
    asyncio.run(main())