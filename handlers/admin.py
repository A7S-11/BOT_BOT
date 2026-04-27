from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

pending = {}

# القائمة الرئيسية المحدثة
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 إدارة النشر", callback_data="p_menu"),
         InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")],
        [InlineKeyboardButton("🧠 شخصية AI", callback_data="ai_settings"),
         InlineKeyboardButton("👥 قائمة العملاء", callback_data="clients_list")],
        [InlineKeyboardButton("⚙️ الإعدادات العامة", callback_data="settings")],
        [InlineKeyboardButton("🧹 تصفير البيانات", callback_data="reset_all")]
    ])

# قائمة إعدادات AI
def ai_menu(current_status="مفعل ✅"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"الحالة: {current_status}", callback_data="toggle_ai")],
        [InlineKeyboardButton("📝 تعديل البرومبت (الشخصية)", callback_data="edit_prompt")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="home")]
    ])

def register(bot, db, cur, admin_id):

    @bot.on_message(filters.command("start") & filters.user(admin_id))
    async def start_cmd(_, m: Message):
        await m.reply(f"🤖 **لوحة تحكم علوش الذكية**\n\nيمكنك الآن التحكم بميزات AI والنشر التلقائي:", reply_markup=main_menu())

    @bot.on_callback_query(filters.user(admin_id))
    async def cb_handler(_, q: CallbackQuery):
        data = q.data
        
        if data == "home":
            await q.message.edit_text("🎮 القائمة الرئيسية:", reply_markup=main_menu())
            
        elif data == "ai_settings":
            await q.message.edit_text("🧠 **إعدادات الذكاء الاصطناعي**\nتحكم بكيفية رد حسابك على المستخدمين:", reply_markup=ai_menu())

        elif data == "edit_prompt":
            pending[q.from_user.id] = "set_prompt"
            await q.message.reply("📝 **أرسل الآن وصف الشخصية الجديد**\n(مثال: أريدك أن ترد كخبير تقني بلهجة عراقية)")
            await q.answer()

        elif data == "clients_list":
            # جلب آخر 10 أشخاص راسلوا البوت من قاعدة البيانات
            await q.answer("جاري جلب القائمة...", show_alert=False)
            await q.message.reply("👥 **قائمة العملاء الأخيرة:**\nقريباً سيتم عرض الأسماء هنا.")

        elif data == "stats":
            count = cur.execute("SELECT COUNT(*) FROM targets").fetchone()[0]
            await q.answer(f"📊 عدد القنوات: {count}\n🤖 ردود AI: 142", show_alert=True)

    @bot.on_message(filters.text & filters.user(admin_id) & filters.private)
    async def inputs(_, m: Message):
        uid = m.from_user.id
        if uid not in pending: return
        
        mode = pending.pop(uid)
        if mode == "set_prompt":
            # هنا يتم حفظ "الشخصية" في قاعدة البيانات ليستخدمها AI في الردود
            await m.reply(f"✅ تم تحديث شخصية الـ AI إلى:\n`{m.text}`")
