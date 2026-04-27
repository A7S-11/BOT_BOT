from pyrogram import filters
import random
import asyncio
import logging

# استيراد الوظائف من الملفات الأساسية
from core.scoring import calculate_score, get_state
from core.style import choose_style, get_best_style
from core.learning import get_best_replies
from ai.engine import generate_reply
from config import REPLY_PROBABILITY

log = logging.getLogger(__name__)

# ذاكرة مؤقتة لحفظ سياق الحديث
MEMORY = {}

def register(app, db, cur):
    """
    تسجيل هاندلر الدردشة مع تمرير قاعدة البيانات والكيرسر.
    """
    
    @app.on_message(filters.text & (filters.group | filters.private))
    async def chat(client, m):
        # ❌ تجاهل البوتات أو الرسائل بدون مستخدم أو رسائلي الشخصية
        if not m.from_user or m.from_user.is_bot or m.from_user.is_self:
            return

        # 🎲 احتمالية الرد في الكروبات (أما في الخاص فيرد دائماً)
        if m.chat.type in ["group", "supergroup"]:
            if random.random() > REPLY_PROBABILITY:
                return

        user_id = m.from_user.id
        text = m.text.strip()

        # ───── MEMORY ─────
        if user_id not in MEMORY:
            MEMORY[user_id] = []
        MEMORY[user_id].append(text)
        history = MEMORY[user_id][-5:] # آخر 5 رسائل

        try:
            # ───── SCORING & STATE ─────
            current_score = calculate_score(text)

            # جلب السكور القديم
            row = cur.execute(
                "SELECT score FROM clients WHERE user_id=?",
                (user_id,)
            ).fetchone()

            total_score = current_score + (row[0] if row else 0)
            state = get_state(total_score)

            # تحديث بيانات العميل
            cur.execute(
                "INSERT OR REPLACE INTO clients (user_id, score, state) VALUES (?, ?, ?)",
                (user_id, total_score, state)
            )

            # ───── STYLE & LEARNING ─────
            style = choose_style(state)
            best_style = get_best_style(cur)
            best_replies = get_best_replies(cur)

            # ───── AI REPLY ─────
            await client.send_chat_action(m.chat.id, "typing")
            
            # توليد الرد من الـ AI
            reply = await generate_reply(
                text=text,
                state=state,
                style=style,
                best_style=best_style,
                memory=history + best_replies,
                cur=cur # تمرير cur إذا كان الـ engine يحتاجه
            )

            # ───── SAVE LEARNING DATA ─────
            cur.execute(
                """
                INSERT INTO learning_data (user_text, bot_reply, state, style)
                VALUES (?, ?, ?, ?)
                """,
                (text, reply, state, style)
            )
            
            # حفظ التغييرات باستخدام كائن الـ db الممرر للدالة
            db.commit() 

            # ───── الرد النهائي ─────
            await m.reply(reply)

        except Exception as e:
            log.error(f"❌ Chat Error: {e}")
            # رد احتياطي بسيط
            # await m.reply("ثواني عيوني، النت يقطع يمي..") 
