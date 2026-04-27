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
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)

# ───── Clients ─────
# ملاحظة: إذا كنت تستخدم String Session للـ Userbot ضيفها هنا
bot = Client(
    "bot_session", 
    api_id=config.API_ID, 
    api_hash=config.API_HASH, 
    bot_token=config.BOT_TOKEN
)

userbot = Client(
    "user_session", 
    api_id=config.API_ID, 
    api_hash=config.API_HASH
)

# ───── Main ─────
async def main():
    # استدعاء قاعدة البيانات
    db, cur = get_db()

    # تسجيل الهاندلرز
    chat_register(bot, cur)
    admin_register(bot, db, cur, config.ADMIN_ID)

    # تشغيل الكلاينت
    log.info("🚀 Starting Clients...")
    await bot.start()
    await userbot.start()

    log.info("🤖 Bot and Userbot are online!")

    # دالة المهام الآمنة (تعديل بسيط لضمان تمرير الـ arguments بشكل صحيح)
    async def safe_task(coro_func, name, *args):
        while True:
            try:
                log.info(f"⏳ Starting task: {name}")
                await coro_func(*args)
            except Exception as e:
                log.error(f"❌ Error in {name}: {e}")
                await asyncio.sleep(10) # انتظار قليل قبل إعادة المحاولة

    # تشغيل المهام الخلفية
    asyncio.create_task(safe_task(publisher, "publisher", userbot, cur))
    asyncio.create_task(safe_task(retarget, "retarget", bot, cur))

    # الحفاظ على البوت يعمل للأبد
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("👋 Bot stopped by user.")
