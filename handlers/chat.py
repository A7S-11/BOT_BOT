from pyrogram import filters
import random
from core.scoring import calculate_score, get_state
from core.style import choose_style, get_best_style
from ai.engine import generate_reply
from config import REPLY_PROBABILITY

MEMORY = {}

def register(app, cur):

    @app.on_message(filters.text)
    async def chat(_, m):

        if random.random() > REPLY_PROBABILITY:
            return

        user_id = m.from_user.id
        text = m.text.lower()

        history = MEMORY.get(user_id, [])
        history.append(text)
        MEMORY[user_id] = history[-5:]

        score = calculate_score(text)

        row = cur.execute("SELECT score FROM clients WHERE user_id=?", (user_id,)).fetchone()
        total = score + (row[0] if row else 0)

        state = get_state(total)

        cur.execute("INSERT OR REPLACE INTO clients VALUES (?, ?, ?)", (user_id, total, state))

        style = choose_style(state)
        best_style = get_best_style(cur)

        reply = await generate_reply(text, state, style, best_style, history)

        cur.execute(
            "INSERT INTO learning_data (user_text, bot_reply, state, style) VALUES (?, ?, ?, ?)",
            (text, reply, state, style)
        )

        await m.reply(reply)