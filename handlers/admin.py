from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

pending = {}

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 إدارة النشر", callback_data="p_menu"),
         InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")],
        [InlineKeyboardButton("🧠 شخصية AI", callback_data="ai_menu")],
        [InlineKeyboardButton("🧹 تصفير البيانات", callback_data="reset")]
    ])

def publish_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ إضافة قناة", callback_data="add_c"),
         InlineKeyboardButton("➕ إضافة نص", callback_data="add_t")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="home")]
    ])

def register(bot, db, cur, admin_id):

    @bot.on_message(filters.command("start") & filters.user(admin_id))
    async def start_cmd(_, m: Message):
        await m.reply("👋 هلا علوش، لوحة التحكم المحدثة وصلت!\nتحكم بنشر حسابك من هنا:", reply_markup=main_menu())

    @bot.on_callback_query(filters.user(admin_id))
    async def cb_handler(_, q: CallbackQuery):
        if q.data == "home":
            await q.message.edit_text("🎮 القائمة الرئيسية:", reply_markup=main_menu())
        elif q.data == "p_menu":
            await q.message.edit_text("📢 إدارة النشر:", reply_markup=publish_menu())
        elif q.data == "add_c":
            pending[q.from_user.id] = "chat"
            await q.message.reply("📌 أرسل يوزر القناة الآن:")
            await q.answer()
        elif q.data == "stats":
            count = cur.execute("SELECT COUNT(*) FROM targets").fetchone()[0]
            await q.answer(f"عدد القنوات: {count}", show_alert=True)

    @bot.on_message(filters.text & filters.user(admin_id) & filters.private)
    async def inputs(_, m: Message):
        uid = m.from_user.id
        if uid not in pending: return
        
        mode = pending.pop(uid)
        if mode == "chat":
            cur.execute("INSERT OR IGNORE INTO targets (id) VALUES (?)", (m.text,))
            db.commit()
            await m.reply(f"✅ تمت إضافة القناة: {m.text}")