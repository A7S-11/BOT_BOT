from pyrogram import filters
import random
from core.scoring import calculate_score, get_state
from core.style import choose_style, get_best_style
from core.learning import get_best_replies
from ai.engine import generate_reply
from config import REPLY_PROBABILITY

MEMORY = {}

def register(app, cur, db):

    # إنشاء الجداول إذا ما موجودة
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        user_id INTEGER PRIMARY KEY,
        score INTEGER,
        state TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS learning_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_text TEXT,
        bot_reply TEXT,
        state TEXT,
        style TEXT
    )
    """)
    db.commit()

    # ✅ رد فقط بالكروبات (مو الخاص)
    @app.on_message(filters.text & filters.group)
    async def chat(_, m):

        # ❌ تجاهل البوتات
        if m.from_user is None or m.from_user.is_bot:
            return

        # 🎲 تقليل الردود
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

        # ───── LEARNING ─────
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
            print("AI Error:", e)
            reply = "صار خلل بسيط، اكتبلي مرة ثانية 🙏"

        # ───── حفظ التعلم ─────
        cur.execute(
            """
            INSERT INTO learning_data (user_text, bot_reply, state, style)
            VALUES (?, ?, ?, ?)
            """,
            (text, reply, state, style)
        )

        db.commit()

        # ───── الرد ─────
        await m.reply(reply)