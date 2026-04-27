import os

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")  # ✅ صححنا الاسم
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # ✅ صححنا الاسم

DELAY_MIN = 60
DELAY_MAX = 120
REPLY_PROBABILITY = 0.6