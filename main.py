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

# إعداد السجلات (Logs)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

# ───── إعدادات المسارات (Railway Volume) ─────
DATA_DIR = "/data"
SESSION_NAME = "user"
SESSION_FILE = f"{SESSION_NAME}.session"

async def main():
    log.info("🚀 Starting Bot...")

    # 1. إدارة ملف السشن (نقل الملف من GitHub إلى المجلد المحمي)
    if os.path.exists(SESSION_FILE) and not os.path.exists(f"{DATA_DIR}/{SESSION_FILE}"):
        try:
            shutil.copy(SESSION_FILE, f"{DATA_DIR}/{SESSION_FILE}")
            log.info(f"✅ Moved {SESSION_FILE} to {DATA_DIR}")
        except Exception as e:
            log.error(f"❌ Failed to move session: {e}")

    # 2. الاتصال بقاعدة البيانات
    try:
        db, cur = get_db()
        log.info("✅ Database connected.")
    except Exception as e:
        log.error(f"🔥 Database error: {e}")
        return

    # 3. تعريف عميل Pyrogram مع مسار السشن بداخل الفوليوم
    # ملاحظة: نستخدم المسار بداخل DATA_DIR لضمان الاستمرارية
    app = Client(
        name=f"{DATA_DIR}/{SESSION_NAME}",
        api_id=config.API_ID,
        api_hash=config.API_HASH
    )

    # 4. تسجيل الهاندلرز (الأدمن والدردشة)
    admin_register(app, db, cur, config.ADMIN_ID)
    chat_register(app, db, cur)

    # 5. بدء تشغيل البوت
    await app.start()
    log.info("💎 Bot is online and connected!")

    # 6. تشغيل المهام الخلفية (Background Tasks)
    # تشغيل الناشر وإعادة الاستهداف كمهام غير متزامنة
    asyncio.create_task(publisher(app, cur))
    asyncio.create_task(retarget(app, cur))

    # 7. الحفاظ على البوت قيد التشغيل (Idle)
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("👋 Bot stopped by user.")
    except Exception as e:
        log.error(f"🔥 Critical error: {e}")
