from pyrogram import filters
import random
import logging
from core.scoring import calculate_score, get_state
from ai.engine import generate_reply # تأكد من وجود engine.py يربط مع Gemini
from config import REPLY_PROBABILITY

log = logging.getLogger(__name__)
MEMORY = {}

def register(app, db, cur):
    @app.on_message(filters.text & (filters.group | filters.private))
    async def chat(client, m):
        if not m.from_user or m.from_user.is_bot or m.from_user.is_self:
            return

        # احتمالية الرد في الكروبات
        if m.chat.type in ["group", "supergroup"] and random.random() > REPLY_PROBABILITY:
            return

        user_id = m.from_user.id
        text = m.text.strip()

        # الذاكرة
        if user_id not in MEMORY: MEMORY[user_id] = []
        MEMORY[user_id].append(text)
        history = MEMORY[user_id][-5:]

        try:
            # السكور والحالة
            current_score = calculate_score(text)
            row = cur.execute("SELECT score FROM clients WHERE user_id=?", (user_id,)).fetchone()
            total_score = current_score + (row[0] if row else 0)
            state = get_state(total_score)

            cur.execute("INSERT OR REPLACE INTO clients (user_id, score, state) VALUES (?, ?, ?)", (user_id, total_score, state))
            db.commit()

            # الرد الذكي
            await client.send_chat_action(m.chat.id, "typing")
            reply = await generate_reply(text=text, state=state, memory=history)
            
            await m.reply(reply)

        except Exception as e:
            log.error(f"❌ Chat Error: {e}")
