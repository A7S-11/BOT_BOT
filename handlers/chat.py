from pyrogram import filters
import random
from core.scoring import calculate_score, get_state
from core.style import choose_style, get_best_style
from core.learning import get_best_replies
from ai.engine import generate_reply
from config import REPLY_PROBABILITY

# 🧠 ذاكرة مؤقتة
MEMORY = {}

def register(app, cur, db):

    @app.on_message(filters.text)
    async def chat(_, m):

        # تقليل الردود (Anti-Spam)
        if random.random() > REPLY_PROBABILITY:
            return

        user_id = m.from_user.id
        text = m.text.lower()

        # ───── MEMORY ─────
        history = MEMORY.get(user_id, [])
        history.append(text)
        MEMORY[user_id] = history[-5:]

        # ───── SCORING ─────
        score = calculate_score(text)

        row = cur.execute(
            "SELECT score FROM clients WHERE user_id=?",
            (user_id,)
        ).fetchone()

        total = score + (row[0] if row else 0)

        state = get_state(total)

        # حفظ العميل
        cur.execute(
            "INSERT OR REPLACE INTO clients VALUES (?, ?, ?)",
            (user_id, total, state)
        )

        # ───── STYLE ─────
        style = choose_style(state)
        best_style = get_best_style(cur)

        # ───── LEARNING DATA ─────
        best_replies = get_best_replies(cur)

        # ───── AI REPLY ─────
        try:
            reply = await generate_reply(
                text=text,
                state=state,
                style=style,
                best_style=best_style,
                memory=history + best_replies
            )
        except Exception as e:
            reply = "صارت مشكلة بسيطة، اكتبلي مرة ثانية 🙏"

        # ───── حفظ التعلم ─────
        cur.execute(
            """
            INSERT INTO learning_data (user_text, bot_reply, state, style)
            VALUES (?, ?, ?, ?)
            """,
            (text, reply, state, style)
        )

        db.commit()

        # ───── إرسال الرد ─────
        await m.reply(reply)