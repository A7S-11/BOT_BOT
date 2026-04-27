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
    log.info("🚀 بدء تشغيل النظام الهجين...")

    # 1. إدارة ملف السشن
    if os.path.exists(SESSION_FILE) and not os.path.exists(f"{DATA_DIR}/{SESSION_FILE}"):
        shutil.copy(SESSION_FILE, f"{DATA_DIR}/{SESSION_FILE}")

    # 2. الاتصال بقاعدة البيانات
    db, cur = get_db()

    # 3. عميل الحساب الشخصي (للنشر والرد التلقائي)
    app = Client(
        name=f"{DATA_DIR}/{SESSION_NAME}",
        api_id=config.API_ID,
        api_hash=config.API_HASH
    )

    # 4. عميل البوت الرسمي (لوحة التحكم بالأزرار الشفافة)
    # تأكد من تعريف BOT_TOKEN في ملف config.py
    bot_app = Client(
        name="bot_admin",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN
    )

    # 5. تسجيل الهاندلرز
    # لوحة التحكم تعمل من خلال البوت الرسمي لتظهر الأزرار الشفافة
    admin_register(bot_app, db, cur, config.ADMIN_ID)
    # الردود تعمل من خلال حسابك الشخصي
    chat_register(app, db, cur)

    # 6. تشغيل العملاء
    await app.start()
    await bot_app.start()
    log.info("💎 الحساب والبوت متصلان وجاهزان!")

    # 7. تشغيل المهام الخلفية (تستخدم حسابك الشخصي)
    asyncio.create_task(publisher(app, cur))
    asyncio.create_task(retarget(app, cur))

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
