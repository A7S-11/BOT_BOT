from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
import logging

log = logging.getLogger(__name__)

# ذاكرة مؤقتة لحفظ حالة الإدخال
pending = {}

# ───── القوائم (Menus) ─────
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 إدارة النشر", callback_data="page_publish")],
        [InlineKeyboardButton("🧠 شخصية AI", callback_data="page_ai")],
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="page_dashboard")],
        [InlineKeyboardButton("👥 قائمة العملاء", callback_data="clients")],
        [InlineKeyboardButton("🧹 تصفير البيانات", callback_data="confirm_reset")]
    ])

def publish_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ إضافة قناة", callback_data="add_chat"),
         InlineKeyboardButton("➕ إضافة نص", callback_data="add_msg")],
        [InlineKeyboardButton("📋 عرض القنوات", callback_data="list_chats"),
         InlineKeyboardButton("📝 عرض النصوص", callback_data="list_msgs")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
    ])

def ai_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("😇 ودي (Friendly)", callback_data="ai_friendly"),
         InlineKeyboardButton("⚡ هجومي (Aggressive)", callback_data="ai_aggressive")],
        [InlineKeyboardButton("🎓 خبير (Expert)", callback_data="ai_expert"),
         InlineKeyboardButton("⏳ استعجال (Scarcity)", callback_data="ai_scarcity")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
    ])

# ───── تسجيل الهاندلرز ─────
def register(bot, db, cur, admin_id):

    @bot.on_message(filters.command("start") & filters.user(admin_id))
    async def start_cmd(_, m: Message):
        await m.reply(f"اهلا بك علوش في لوحة التحكم 🤖", reply_markup=main_menu())

    @bot.on_callback_query(filters.user(admin_id))
    async def callback_handler(_, q: CallbackQuery):
        data = q.data

        if data == "back":
            await q.message.edit("🎮 لوحة التحكم الأساسية:", reply_markup=main_menu())

        elif data == "page_publish":
            await q.message.edit("📢 إدارة النشر التلقائي بالكروبات:", reply_markup=publish_menu())

        elif data == "page_ai":
            await q.message.edit("🧠 اختر نبرة صوت البوت عند الرد:", reply_markup=ai_menu())

        elif data == "page_dashboard":
            targets = cur.execute("SELECT COUNT(*) FROM targets").fetchone()[0]
            msgs = cur.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            clients = cur.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
            
            text = f"📊 **Dashboard**\n\n🎯 القنوات: {targets}\n📝 النصوص: {msgs}\n👥 العملاء: {clients}"
            await q.message.edit(text, reply_markup=main_menu())

        elif data.startswith("ai_"):
            style = data.split("_")[1]
            cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('ai_style', ?)", (style,))
            db.commit()
            await q.answer(f"✅ تم تفعيل أسلوب الـ {style}", show_alert=True)

        elif data == "add_chat":
            pending[q.from_user.id] = "chat"
            await q.message.reply("📌 أرسل الآن آيدي القناة أو اليوزرنيم (مثل: -100123 أو @my_group)")

        elif data == "add_msg":
            pending[q.from_user.id] = "msg"
            await q.message.reply("📝 أرسل الآن نص الإعلان الجديد:")

        elif data == "list_chats":
            rows = cur.execute("SELECT id FROM targets").fetchall()
            txt = "🎯 **القنوات المضافة:**\n\n" + ("\n".join([f"`{r[0]}`" for r in rows]) if rows else "❌ فارغة")
            await q.message.reply(txt)

        elif data == "list_msgs":
            rows = cur.execute("SELECT id, content FROM messages").fetchall()
            txt = "📝 **النصوص المضافة:**\n\n" + ("\n---\n".join([f"{r[0]}- {r[1]}" for r in rows]) if rows else "❌ فارغة")
            await q.message.reply(txt)

        elif data == "clients":
            rows = cur.execute("SELECT user_id, score, state FROM clients ORDER BY score DESC LIMIT 15").fetchall()
            txt = "👥 **أهم 15 عميل مهتم:**\n\nID | Score | State\n"
            txt += "\n".join([f"`{u}` | {s} | {st}" for u, s, st in rows]) if rows else "❌ لا يوجد بيانات"
            await q.message.edit(txt, reply_markup=main_menu())

    @bot.on_message(filters.text & filters.user(admin_id) & filters.private)
    async def handle_inputs(_, m: Message):
        user_id = m.from_user.id
        if user_id not in pending:
            return

        mode = pending.pop(user_id)
        val = m.text.strip()

        try:
            if mode == "chat":
                cur.execute("INSERT OR IGNORE INTO targets (id) VALUES (?)", (val,))
                db.commit()
                await m.reply(f"✅ تمت إضافة الهدف: `{val}`")
            
            elif mode == "msg":
                cur.execute("INSERT INTO messages (content) VALUES (?)", (val,))
                db.commit()
                await m.reply("✅ تم حفظ النص بنجاح.")
        except Exception as e:
            await m.reply(f"❌ حدث خطأ: {e}")
