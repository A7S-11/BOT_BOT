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

# ───── تسجيل الهاندلرز ─────
def register(bot, db, cur, admin_id):

    @bot.on_message(filters.command("start") & filters.user(admin_id))
    async def start_cmd(_, m: Message):
        # هنا نرسل القائمة الرئيسية مع الأزرار
        await m.reply(f"اهلا بك علوش في لوحة التحكم 🤖", reply_markup=main_menu())

    @bot.on_callback_query(filters.user(admin_id))
    async def callback_handler(_, q: CallbackQuery):
        data = q.data

        if data == "back":
            await q.message.edit_text("🎮 لوحة التحكم الأساسية:", reply_markup=main_menu())

        elif data == "page_publish":
            # تحديث الرسالة لتظهر أزرار "إضافة قناة" و "إضافة نص"
            await q.message.edit_text("📢 إدارة النشر التلقائي:\n\nاضغط على الأزرار أدناه للإدارة:", reply_markup=publish_menu())

        elif data == "add_chat":
            pending[q.from_user.id] = "chat"
            await q.answer("أرسل اليوزر الآن")
            await q.message.reply("📌 أرسل الآن يوزر القناة (مثلاً @user) أو الآيدي:")

        elif data == "add_msg":
            pending[q.from_user.id] = "msg"
            await q.answer("أرسل النص الآن")
            await q.message.reply("📝 أرسل الآن نص الإعلان الجديد:")

    @bot.on_message(filters.text & filters.user(admin_id) & filters.private)
    async def handle_inputs(_, m: Message):
        user_id = m.from_user.id
        if user_id not in pending:
            return

        mode = pending.pop(user_id)
        val = m.text.strip()

        if mode == "chat":
            cur.execute("INSERT OR IGNORE INTO targets (id) VALUES (?)", (val,))
            db.commit()
            await m.reply(f"✅ تمت إضافة القناة `{val}` بنجاح.")
        
        elif mode == "msg":
            cur.execute("INSERT INTO messages (content) VALUES (?)", (val,))
            db.commit()
            await m.reply("✅ تم حفظ النص بنجاح.")