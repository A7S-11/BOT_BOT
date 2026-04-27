from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

pending = {}

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 إضافة نص", callback_data="add_msg"),
         InlineKeyboardButton("➕ إضافة قناة", callback_data="add_chat")],
        [InlineKeyboardButton("📋 عرض النصوص", callback_data="list_msgs"),
         InlineKeyboardButton("📊 عرض القنوات", callback_data="list_chats")],
        [InlineKeyboardButton("❌ حذف نص", callback_data="del_msg"),
         InlineKeyboardButton("❌ حذف قناة", callback_data="del_chat")],
        [InlineKeyboardButton("⚙️ حالة النشر: شغال ✅", callback_data="toggle_pub")],
        [InlineKeyboardButton("🔙 إيقاف ⛔", callback_data="stop_pub"),
         InlineKeyboardButton("▶️ تشغيل", callback_data="start_pub")]
    ])

def register(bot, db, cur, admin_id):

    @bot.on_message(filters.command("start") & filters.user(admin_id))
    async def start_cmd(_, m: Message):
        await m.reply(f"هلا علوش، لوحة التحكم المحدثة 🤚\n\nتحكم بنشر حسابك الشخصي من هنا:", reply_markup=main_menu())

    @bot.on_callback_query(filters.user(admin_id))
    async def cb_handler(_, q: CallbackQuery):
        data = q.data
        if data == "add_chat":
            pending[q.from_user.id] = "chat"
            await q.message.reply("📌 أرسل الآن يوزر القناة أو الآيدي:")
            await q.answer()
        elif data == "add_msg":
            pending[q.from_user.id] = "msg"
            await q.message.reply("📝 أرسل الآن نص الإعلان الجديد:")
            await q.answer()
        # يمكنك إضافة بقية منطق الأزرار هنا (عرض، حذف، إلخ)

    @bot.on_message(filters.text & filters.user(admin_id) & filters.private)
    async def input_handler(_, m: Message):
        uid = m.from_user.id
        if uid not in pending: return
        
        mode = pending.pop(uid)
        if mode == "chat":
            cur.execute("INSERT OR IGNORE INTO targets (id) VALUES (?)", (m.text,))
            db.commit()
            await m.reply(f"✅ تمت إضافة القناة: {m.text}")
        elif mode == "msg":
            cur.execute("INSERT INTO messages (content) VALUES (?)", (m.text,))
            db.commit()
            await m.reply("✅ تم حفظ نص الإعلان الجديد.")
