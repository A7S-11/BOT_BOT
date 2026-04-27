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
        [InlineKeyboardButton("➕ قناة", callback_data="add_chat"),
         InlineKeyboardButton("➕ نص", callback_data="add_msg")],
        [InlineKeyboardButton("📊 القنوات", callback_data="list_chats"),
         InlineKeyboardButton("📋 النصوص", callback_data="list_msgs")],
        [InlineKeyboardButton("▶️ تشغيل", callback_data="run"),
         InlineKeyboardButton("⛔ إيقاف", callback_data="stop")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
    ])

def ai_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("😎 Friendly", callback_data="ai_friendly"),
         InlineKeyboardButton("🔥 Aggressive", callback_data="ai_aggressive")],
        [InlineKeyboardButton("🧠 Expert", callback_data="ai_expert"),
         InlineKeyboardButton("⏳ Scarcity", callback_data="ai_scarcity")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
    ])

# ───── التسجيل ─────

def register(bot, cur, db, admin_id):
    global ADMIN_ID
    ADMIN_ID = admin_id

    # تأكد من الجداول
    cur.execute("CREATE TABLE IF NOT EXISTS clients (user_id TEXT, score INT, state TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    db.commit()

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

        if data == "page_publish":
            await q.message.edit("📢 إدارة النشر", reply_markup=publish_menu())

        elif data == "page_dashboard":
            targets = cur.execute("SELECT COUNT(*) FROM targets").fetchone()[0]
            msgs = cur.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            clients = cur.execute("SELECT COUNT(*) FROM clients").fetchone()[0]

            text = f"""
📊 Dashboard

📢 قنوات: {targets}
📝 نصوص: {msgs}
👥 عملاء: {clients}
"""
            await q.message.edit(text, reply_markup=main_menu())

        elif data == "page_ai":
            await q.message.edit("🧠 اختر شخصية AI", reply_markup=ai_menu())

        elif data == "back":
            await q.message.edit("🎮 لوحة التحكم", reply_markup=main_menu())

        elif data.startswith("ai_"):
            style = data.split("_")[1]
            cur.execute("INSERT OR REPLACE INTO settings VALUES ('ai_style', ?)", (style,))
            db.commit()
            await q.answer(f"✅ تم تغيير AI إلى {style}", True)

        elif data == "add_chat":
            pending[q.from_user.id] = "chat"
            await q.message.reply("📌 أرسل آيدي القناة (مثال: -100xxxx)")

        elif data == "add_msg":
            pending[q.from_user.id] = "msg"
            await q.message.reply("📝 أرسل النص")

        elif data == "list_chats":
            rows = cur.execute("SELECT id FROM targets").fetchall()
            txt = "\n".join([r[0] for r in rows]) if rows else "❌ لا يوجد"
            await q.message.reply(txt)

        elif data == "list_msgs":
            rows = cur.execute("SELECT content FROM messages").fetchall()
            txt = "\n\n".join([r[0] for r in rows]) if rows else "❌ لا يوجد"
            await q.message.reply(txt)

        elif data == "run":
            bot.running = True
            await q.answer("▶️ تم التشغيل", True)

        elif data == "stop":
            bot.running = False
            await q.answer("⛔ تم الإيقاف", True)

        elif data == "clients":
            rows = cur.execute("SELECT user_id, score, state FROM clients ORDER BY score DESC LIMIT 10").fetchall()
            txt = "\n".join([f"{u} | {s} | {st}" for u, s, st in rows]) if rows else "❌ لا يوجد"
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

        try:
            if mode == "chat":
                if not text.startswith("-100"):
                    return await m.reply("❌ لازم آيدي قناة صحيح")

                cur.execute("INSERT INTO targets VALUES (?)", (text,))
                db.commit()
                await m.reply("✅ تمت إضافة القناة")

            elif mode == "msg":
                if len(text) < 5:
                    return await m.reply("❌ النص قصير")

                cur.execute("INSERT INTO messages VALUES (?)", (text,))
                db.commit()
                await m.reply("✅ تم حفظ النص")

        except Exception as e:
            await m.reply(f"❌ خطأ: {e}")

        pending.pop(m.from_user.id, None)