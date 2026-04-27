import os

# ───── Telegram ─────
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ───── Admin ─────
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# ───── OpenAI ─────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ───── Settings ─────
DELAY_MIN = int(os.getenv("DELAY_MIN", 60))
DELAY_MAX = int(os.getenv("DELAY_MAX", 120))
REPLY_PROBABILITY = float(os.getenv("REPLY_PROBABILITY", 0.6))


# ───── تحقق من القيم ─────
if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("❌ لازم تضيف API_ID / API_HASH / BOT_TOKEN")

if not ADMIN_ID:
    raise ValueError("❌ لازم تضيف ADMIN_ID")

if not OPENAI_API_KEY:
    print("⚠️ OpenAI API Key مو موجود (البوت راح يشتغل بدون AI)")