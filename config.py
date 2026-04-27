import os

# ملاحظة: حذفنا استدعاء load_dotenv لتجنب خطأ ModuleNotFoundError في Railway
# بما أن Railway يقرأ المتغيرات مباشرة من الـ Environment Variables

# ───── Telegram ─────
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ───── Admin ─────
ADMIN_ID = os.getenv("ADMIN_ID")

# ───── Google Gemini AI ─────
# استبدلنا OpenAI بـ Gemini كما في تحديثاتك الأخيرة
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ───── Settings ─────
DELAY_MIN = int(os.getenv("DELAY_MIN", 60))
DELAY_MAX = int(os.getenv("DELAY_MAX", 120))
REPLY_PROBABILITY = float(os.getenv("REPLY_PROBABILITY", 0.6))

# ───── تحقق من القيم الأساسية ─────
if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError("❌ نقص في بيانات التليجرام: API_ID, API_HASH, or BOT_TOKEN missing!")

# تحويل القيم الرقمية
API_ID = int(API_ID)
ADMIN_ID = int(ADMIN_ID) if ADMIN_ID else None

if not GEMINI_API_KEY:
    print("⚠️ تحذير: GEMINI_API_KEY غير محدد، ميزات الـ AI لن تعمل.")
