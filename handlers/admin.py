from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

pending = {}

# القائمة الرئيسية
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 إدارة النشر", callback_data="p_menu"),
         InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")],
        [InlineKeyboardButton("🧠 شخصية AI", callback_data="ai_settings"),
         InlineKeyboardButton("👥 قائمة العملاء", callback_data="clients_list")],
        [InlineKeyboardButton("⚙️ الإعدادات العامة", callback_data="settings")],
        [InlineKeyboardButton("🧹 تصفير البيانات", callback_data="reset_all")]
    ])

# قائمة إدارة النشر
def publish_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ إضافة قناة", callback_data="add_c"),
         InlineKeyboardButton("➕ إضافة نص", callback_data="add_t")],
        [InlineKeyboardButton("📋 عرض القنوات", callback_data="view_c")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="home")]
    ])

def register(bot, db, cur, admin_id):

    @bot.on_message(filters.command("start") & filters.user(admin_id))
    async def start_cmd(_, m: Message):
        await m.reply(f"🤖 **لوحة تحكم علوش الذكية**\n\nيمكنك الآن التحكم بميزات AI والنشر التلقائي:", reply_markup=main_menu())

    @bot.on_callback_query(filters.user(admin_id))
    async def cb_handler(_, q: CallbackQuery):
        data = q.data
        
        # التنقل بين القوائم
        if data == "home":
            await q.edit_message_text("🎮 القائمة الرئيسية:", reply_markup=main_menu())
            
        elif data == "p_menu":
            await q.edit_message_text("📢 **إدارة النشر التلقائي**\nأضف القنوات والنصوص التي تريد من حسابك نشرها:", reply_markup=publish_menu())

        elif data == "settings":
            await q.edit_message_text("⚙️ **الإعدادات العامة**\nتحكم بوضع الحساب والخصوصية:", reply_markup=main_menu())

        elif data == "ai_settings":
            await q.edit_message_text("🧠 **إعدادات شخصية AI**\nتعديل طريقة رد الحساب على الرسائل:", reply_markup=main_menu())

        # عمليات الإضافة
        elif data == "add_c":
            pending[q.from_user.id] = "chat"
            await q.message.reply("📌 أرسل يوزر القناة الآن (مثال: @username):")
            await q.answer()

        elif data == "add_t":
            pending[q.from_user.id] = "text"
            await q.message.reply("📝 أرسل نص الإعلان الجديد:")
            await q.answer()

        elif data == "stats":
            count = cur.execute("SELECT COUNT(*) FROM targets").fetchone()[0]
            await q.answer(f"📊 عدد القنوات المضافة حالياً: {count}", show_alert=True)

    @bot.on_message(filters.text & filters.user(admin_id) & filters.private)
    async def inputs(_, m: Message):
        uid = m.from_user.id
        if uid not in pending: return
        
        mode = pending.pop(uid)
        if mode == "chat":
            cur.execute("INSERT OR IGNORE INTO targets (id) VALUES (?)", (m.text,))
            db.commit()
            await m.reply(f"✅ تمت إضافة القناة بنجاح: {m.text}")
        elif mode == "text":
            cur.execute("INSERT INTO messages (content) VALUES (?)", (m.text,))
            db.commit()
            await m.reply("✅ تم حفظ النص الجديد للنشر التلقائي.")
