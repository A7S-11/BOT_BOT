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
    log.info("🚀 بدء تشغيل البوت...")

    # 1. إدارة ملف السشن
    if os.path.exists(SESSION_FILE) and not os.path.exists(f"{DATA_DIR}/{SESSION_FILE}"):
        try:
            shutil.copy(SESSION_FILE, f"{DATA_DIR}/{SESSION_FILE}")
            log.info(f"✅ تم نقل ملف {SESSION_FILE} إلى {DATA_DIR}")
        except Exception as e:
            log.error(f"❌ فشل نقل ملف السشن: {e}")

    # 2. الاتصال بقاعدة البيانات
    try:
        db, cur = get_db()
        log.info("✅ تم الاتصال بقاعدة البيانات")
    except Exception as e:
        log.error(f"🔥 خطأ في قاعدة البيانات: {e}")
        return

    # 3. تعريف عميل Pyrogram
    app = Client(
        name=f"{DATA_DIR}/{SESSION_NAME}",
        api_id=config.API_ID,
        api_hash=config.API_HASH
    )

    # 4. تسجيل الهاندلرز (تأكد من تمرير المتغيرات المطلوبة فقط)
    # ملاحظة: دالة الأدمن تحتاج (bot, db, cur, admin_id)
    admin_register(app, db, cur, config.ADMIN_ID)
    
    # ملاحظة: دالة الدردشة تحتاج (bot, db, cur)
    chat_register(app, db, cur)

    # 5. بدء تشغيل البوت
    await app.start()
    log.info("💎 البوت الآن متصل وشغال!")

    # 6. تشغيل المهام الخلفية
    asyncio.create_task(publisher(app, cur))
    asyncio.create_task(retarget(app, cur))

    # 7. الحفاظ على البوت قيد التشغيل
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("👋 تم إيقاف البوت.")
    except Exception as e:
        log.error(f"🔥 خطأ حرج: {e}")