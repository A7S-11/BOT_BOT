import os
import shutil
import asyncio
import logging
from pyrogram import Client

# استيراد الإعدادات وقاعدة البيانات
import config
from database.db import get_db

# استيراد الهاندلرز
from handlers.admin import register as admin_register
from handlers.chat import register as chat_register

# استيراد المهام الخلفية
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

    # 3. عميل الحساب الشخصي (للردود والنشر)
    app = Client(
        name=f"{DATA_DIR}/{SESSION_NAME}",
        api_id=config.API_ID,
        api_hash=config.API_HASH
    )

    # 4. عميل البوت الرسمي (للوحة التحكم والأزرار)
    # تأكد من إضافة BOT_TOKEN في ملف config.py أو Railway
    bot_app = Client(
        name="bot_admin",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN 
    )

    # 5. تسجيل الهاندلرز
    # لوحة التحكم تشتغل على البوت الرسمي
    admin_register(bot_app, db, cur, config.ADMIN_ID)
    
    # الرد التلقائي يشتغل على حسابك الشخصي
    chat_register(app, db, cur)

    # 6. تشغيل العملاء
    await app.start()
    await bot_app.start()
    log.info("💎 الحساب والبوت الآن متصلان!")

    # 7. تشغيل مهام النشر (تستخدم حسابك الشخصي)
    asyncio.create_task(publisher(app, cur))
    asyncio.create_task(retarget(app, cur))

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())