from pyrogram import filters
import random
import asyncio
from core.scoring import calculate_score, get_state
from core.style import choose_style, get_best_style
from core.learning import get_best_replies
from ai.engine import generate_reply
from config import REPLY_PROBABILITY

# ذاكرة مؤقتة لحفظ سياق الحديث
MEMORY = {}

def register(app, cur):
    # ملاحظة: شلنا إنشاء الجداول لأنها موجودة أصلاً بملف db.py
    
    @app.on_message(filters.text & filters.group)
    async def chat(client, m):

        # ❌ تجاهل البوتات أو الرسائل بدون مستخدم
        if not m.from_user or m.from_user.is_bot:
            return

        # 🎲 احتمالية الرد (لتقليل الإزعاج في الكروبات)
        if random.random() > REPLY_PROBABILITY:
            return

        user_id = m.from_user.id
        text = m.text.strip().lower()

        # ───── MEMORY ─────
        if user_id not in MEMORY:
            MEMORY[user_id] = []
        MEMORY[user_id].append(text)
        # الاحتفاظ بآخر 5 رسائل فقط للسياق
        history = MEMORY[user_id][-5:]

        # ───── SCORING & STATE ─────
        # حساب النقاط بناءً على نص الرسالة
        current_score = calculate_score(text)

        # جلب البيانات الحالية للمستخدم
        row = cur.execute(
            "SELECT score FROM clients WHERE user_id=?",
            (user_id,)
        ).fetchone()

        total_score = current_score + (row[0] if row else 0)
        state = get_state(total_score)

        # تحديث بيانات العميل (استخدام INSERT OR REPLACE لضمان عدم التكرار)
        cur.execute(
            "INSERT OR REPLACE INTO clients (user_id, score, state) VALUES (?, ?, ?)",
            (user_id, total_score, state)
        )

        # ───── STYLE & LEARNING ─────
        style = choose_style(state)
        best_style = get_best_style(cur)
        best_replies = get_best_replies(cur)

        # ───── AI REPLY ─────
        # إظهار حالة "يُكتب الآن..." لإعطاء طابع واقعي
        await client.send_chat_action(m.chat.id, "typing")
        
        try:
            reply = await generate_reply(
                text=text,
                state=state,
                style=style,
                best_style=best_style,
                memory=history + best_replies
            )
        except Exception as e:
            print(f"❌ AI Error: {e}")
            # رد احتياطي في حال فشل الـ AI
            reply = random.choice([
                "ما فهمت قصدك، وضحلي أكثر؟",
                "ثواني وارجعلك، النت ضيف يمي..",
                "ها عيوني؟"
            ])

        # ───── SAVE LEARNING DATA ─────
        cur.execute(
            """
            INSERT INTO learning_data (user_text, bot_reply, state, style)
            VALUES (?, ?, ?, ?)
            """,
            (text, reply, state, style)
        )
        
        # حفظ التغييرات في قاعدة البيانات
        # ملاحظة: الـ commit يفضل يكون هنا لضمان حفظ بيانات الـ learning
        m._client.db_conn.commit() 

        # ───── الرد النهائي ─────
        await m.reply(reply)
