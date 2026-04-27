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
from core.retargeting import retarget

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

DATA_DIR = "/data"
SESSION_NAME = "user"
SESSION_FILE = f"{SESSION_NAME}.session"

async def main():
    log.info("🚀 تشغيل النظام الهجين: لوحة شفافة + نشر تلقائي...")

    # نقل ملف السشن لمجلد البيانات في Railway
    if os.path.exists(SESSION_FILE) and not os.path.exists(f"{DATA_DIR}/{SESSION_FILE}"):
        shutil.copy(SESSION_FILE, f"{DATA_DIR}/{SESSION_FILE}")

    db, cur = get_db()

    # عميل الحساب الشخصي (user_session) - للنشر والرد
    app = Client(
        name=f"{DATA_DIR}/{SESSION_NAME}",
        api_id=config.API_ID,
        api_hash=config.API_HASH
    )

    # عميل البوت الرسمي (bot_admin) - لعرض الأزرار الشفافة
    bot_app = Client(
        name="bot_admin",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN
    )

    # تسجيل اللوحة على بوت التوكن والردود على حسابك
    admin_register(bot_app, db, cur, config.ADMIN_ID)
    chat_register(app, db, cur)

    await app.start()
    await bot_app.start()
    log.info("✅ النظام متصل: اللوحة تعمل عبر البوت الرسمي!")

    # تشغيل مهام النشر الخلفية باستخدام حسابك
    asyncio.create_task(publisher(app, cur))
    asyncio.create_task(retarget(app, cur))

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
