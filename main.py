import os
import shutil
import asyncio
import logging
from pyrogram import Client
import config
from database.db import get_db
from handlers.admin import register as admin_register
from handlers.chat import register as chat_register
from core.publisher import publisher

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

DATA_DIR = "/data"
SESSION_NAME = "user"

async def main():
    log.info("🚀 بدء تشغيل بوت علوش المطور...")
    
    if os.path.exists(f"{SESSION_NAME}.session") and not os.path.exists(f"{DATA_DIR}/{SESSION_NAME}.session"):
        shutil.copy(f"{SESSION_NAME}.session", f"{DATA_DIR}/{SESSION_NAME}.session")

    db, cur = get_db()

    # عميل الحساب الشخصي
    app = Client(name=f"{DATA_DIR}/{SESSION_NAME}", api_id=config.API_ID, api_hash=config.API_HASH)

    # عميل البوت الرسمي للوحة التحكم
    bot_app = Client(name="bot_admin", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)

    # تسجيل الميزات
    admin_register(bot_app, db, cur, config.ADMIN_ID)
    chat_register(app, db, cur)

    await app.start()
    await bot_app.start()
    
    log.info("✅ الحساب والبوت متصلان والرد الذكي شغال!")

    # تشغيل مهمة النشر
    asyncio.create_task(publisher(app, cur))

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
