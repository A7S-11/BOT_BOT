import os
from dotenv import load_dotenv

# لضمان قراءة ملف الـ .env محلياً (Railway سيتجاهلها ويقرأ الـ Variables مباشرة)
load_dotenv()

# ───── Telegram ─────
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ───── Admin ─────
ADMIN_ID = os.getenv("ADMIN_ID")

# ───── OpenAI ─────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ───── Settings ─────
# استخدمنا 60 و 120 كقيم افتراضية في حال لم يتم تحديدها
DELAY_MIN = int(os.getenv("DELAY_MIN", 60))
DELAY_MAX = int(os.getenv("DELAY_MAX", 120))
REPLY_PROBABILITY = float(os.getenv("REPLY_PROBABILITY", 0.6))

# ───── تحقق من القيم الأساسية ─────
if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError("❌ نقص في بيانات التليجرام: API_ID, API_HASH, or BOT_TOKEN missing!")

if not ADMIN_ID:
    print("⚠️ تحذير: ADMIN_ID غير محدد، قد لا تعمل بعض ميزات التحكم.")

# تحويل القيم الرقمية بعد التأكد من وجودها
API_ID = int(API_ID)
ADMIN_ID = int(ADMIN_ID) if ADMIN_ID else None

if not OPENAI_API_KEY:
    print("⚠️ OpenAI API Key مو موجود (البوت راح يشتغل بدون AI)")
