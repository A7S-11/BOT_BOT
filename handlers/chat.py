from pyrogram import filters
import random
import logging
import google.generativeai as genai
from os import environ
from core.scoring import calculate_score, get_state
from config import REPLY_PROBABILITY

log = logging.getLogger(__name__)

# إعداد Gemini
genai.configure(api_key=environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

MEMORY = {}

def register(app, db, cur):
    @app.on_message(filters.text & (filters.group | filters.private))
    async def chat(client, m):
        if not m.from_user or m.from_user.is_bot or m.from_user.is_self:
            return

        user_id = m.from_user.id
        user_name = m.from_user.first_name or "عميل"
        text = m.text.strip()

        # احتمالية الرد
        if m.chat.type in ["group", "supergroup"] and random.random() > REPLY_PROBABILITY:
            return

        try:
            # تحديث سياق الحديث
            if user_id not in MEMORY: MEMORY[user_id] = []
            MEMORY[user_id].append(text)
            history = "\n".join(MEMORY[user_id][-5:])

            # حساب السكور والحالة
            current_score = calculate_score(text)
            row = cur.execute("SELECT score FROM clients WHERE user_id=?", (user_id,)).fetchone()
            total_score = current_score + (row[0] if row else 0)
            state = get_state(total_score)

            # تخزين بيانات العميل (حل مشكلة الخطأ بالاسم)
            cur.execute("""
                INSERT OR REPLACE INTO clients (user_id, name, score, state) 
                VALUES (?, ?, ?, ?)
            """, (user_id, str(user_name), total_score, state))
            db.commit()

            # توليد رد AI باستخدام Gemini
            await client.send_chat_action(m.chat.id, "typing")
            prompt = f"أنت علوش، رد بلهجة عراقية. الحالة: {state}. السياق: {history}\nالمستخدم: {text}"
            response = model.generate_content(prompt)
            reply_text = response.text if response.text else "يا هلا بيك عيوني"

            await m.reply(reply_text)

        except Exception as e:
            log.error(f"❌ Chat Error: {e}")
