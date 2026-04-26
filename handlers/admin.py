from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ADMIN_ID = None
pending = {}

# ───── القوائم ─────

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 النشر", callback_data="page_publish")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="page_dashboard")],
        [InlineKeyboardButton("🧠 AI", callback_data="page_ai")],
        [InlineKeyboardButton("👥 العملاء", callback_data="clients")]
    ])

def publish_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ قناة", "add_chat"),
         InlineKeyboardButton("➕ نص", "add_msg")],
        [InlineKeyboardButton("📊 القنوات", "list_chats"),
         InlineKeyboardButton("📋 النصوص", "list_msgs")],
        [InlineKeyboardButton("▶️ تشغيل", "run"),
         InlineKeyboardButton("⛔ إيقاف", "stop")],
        [InlineKeyboardButton("🔙 رجوع", "back")]
    ])

def ai_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("😎 Friendly", "ai_friendly"),
         InlineKeyboardButton("🔥 Aggressive", "ai_aggressive")],
        [InlineKeyboardButton("🧠 Expert", "ai_expert"),
         InlineKeyboardButton("⏳ Scarcity", "ai_scarcity")],
        [InlineKeyboardButton("🔙 رجوع", "back")]
    ])

# ───── التسجيل ─────

def register(bot, cur, db, admin_id):
    global ADMIN_ID
    ADMIN_ID = admin_id

    # ───── START ─────
    @bot.on_message(filters.command("start"))
    async def start(_, m):
        if m.from_user.id != ADMIN_ID:
            return await m.reply("⛔ غير مصرح")

        await m.reply("🎮 لوحة التحكم", reply_markup=main_menu())

    # ───── الأزرار ─────
    @bot.on_callback_query()
    async def buttons(_, q):

        if q.from_user.id != ADMIN_ID:
            return await q.answer("⛔", True)

        data = q.data

        # ───── صفحات ─────
        if data == "page_publish":
            await q.message.edit("📢 إدارة النشر", reply_markup=publish_menu())

        elif data == "page_dashboard":
            targets = cur.execute("SELECT COUNT(*) FROM targets").fetchone()[0]
            msgs = cur.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            clients = cur.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
            deals = cur.execute("SELECT COUNT(*) FROM learning_data WHERE success=1").fetchone()[0]

            text = f"""
📊 Dashboard

📢 قنوات: {targets}
📝 نصوص: {msgs}
👥 عملاء: {clients}
💰 صفقات: {deals}
"""
            await q.message.edit(text, reply_markup=main_menu())

        elif data == "page_ai":
            await q.message.edit("🧠 اختر شخصية AI", reply_markup=ai_menu())

        elif data == "back":
            await q.message.edit("🎮 لوحة التحكم", reply_markup=main_menu())

        # ───── AI Style ─────
        elif data.startswith("ai_"):
            style = data.split("_")[1]

            cur.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """)

            cur.execute("INSERT OR REPLACE INTO settings VALUES ('ai_style', ?)", (style,))
            db.commit()

            await q.answer(f"✅ تم تغيير الأسلوب إلى {style}", True)

        # ───── إضافة قناة ─────
        elif data == "add_chat":
            pending[q.from_user.id] = "chat"
            await q.message.reply("📌 أرسل آيدي أو يوزر")

        # ───── إضافة نص ─────
        elif data == "add_msg":
            pending[q.from_user.id] = "msg"
            await q.message.reply("📝 أرسل النص")

        # ───── عرض القنوات ─────
        elif data == "list_chats":
            rows = cur.execute("SELECT id FROM targets").fetchall()
            txt = "\n".join([r[0] for r in rows]) if rows else "❌ لا يوجد"
            await q.message.reply(txt)

        # ───── عرض النصوص ─────
        elif data == "list_msgs":
            rows = cur.execute("SELECT content FROM messages").fetchall()
            txt = "\n\n".join([r[0] for r in rows]) if rows else "❌ لا يوجد"
            await q.message.reply(txt)

        # ───── تشغيل ─────
        elif data == "run":
            bot.running = True
            await q.answer("▶️ شغال", True)

        elif data == "stop":
            bot.running = False
            await q.answer("⛔ متوقف", True)

        # ───── العملاء ─────
        elif data == "clients":
            rows = cur.execute("SELECT user_id, score, state FROM clients ORDER BY score DESC LIMIT 10").fetchall()
            txt = "\n".join([f"{u} | {s} | {st}" for u, s, st in rows]) if rows else "❌"
            await q.message.edit("👥 العملاء:\n" + txt, reply_markup=main_menu())

    # ───── إدخال النص ─────
    @bot.on_message(filters.text)
    async def input_handler(_, m):

        if m.from_user.id != ADMIN_ID:
            return

        mode = pending.get(m.from_user.id)
        if not mode:
            return

        text = m.text.strip()

        if mode == "chat":
            cur.execute("INSERT INTO targets VALUES (?)", (text,))
            db.commit()
            await m.reply("✅ تمت إضافة القناة")

        elif mode == "msg":
            cur.execute("INSERT INTO messages VALUES (?)", (text,))
            db.commit()
            await m.reply("✅ تم حفظ النص")

        pending[m.from_user.id] = None