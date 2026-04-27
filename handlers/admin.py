from pyrogram import filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
import logging

log = logging.getLogger(__name__)

# ذاكرة مؤقتة لحفظ حالة الإدخال
pending = {}

# ───── القوائم (Keyboard) ─────
# استخدمنا ReplyKeyboardMarkup بدلاً من Inline لضمان ظهورها لك
def main_menu():
    return ReplyKeyboardMarkup([
        ["📢 إدارة النشر", "🧠 شخصية AI"],
        ["📊 الإحصائيات", "👥 قائمة العملاء"],
        ["🧹 تصفير البيانات"]
    ], resize_keyboard=True)

def publish_menu():
    return ReplyKeyboardMarkup([
        ["➕ إضافة قناة", "➕ إضافة نص"],
        ["📋 عرض القنوات", "📝 عرض النصوص"],
        ["🔙 رجوع"]
    ], resize_keyboard=True)

# ───── تسجيل الهاندلرز ─────
def register(bot, db, cur, admin_id):

    @bot.on_message(filters.command("start") & filters.user(admin_id))
    async def start_cmd(_, m: Message):
        await m.reply("اهلا بك علوش، تم تفعيل لوحة التحكم بالكيبورد:", reply_markup=main_menu())

    @bot.on_message(filters.text & filters.user(admin_id) & filters.private)
    async def handle_admin_logic(_, m: Message):
        user_id = m.from_user.id
        text = m.text

        # التنقل بين القوائم
        if text == "📢 إدارة النشر":
            await m.reply("قائمة النشر التلقائي:", reply_markup=publish_menu())
        
        elif text == "🔙 رجوع":
            await m.reply("العودة للقائمة الرئيسية:", reply_markup=main_menu())

        elif text == "📊 الإحصائيات":
            targets = cur.execute("SELECT COUNT(*) FROM targets").fetchone()[0]
            msgs = cur.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            await m.reply(f"📊 الإحصائيات الحالية:\n🎯 قنوات: {targets}\n📝 نصوص: {msgs}")

        # منطق الإضافة
        elif text == "➕ إضافة قناة":
            pending[user_id] = "chat"
            await m.reply("📌 أرسل الآن يوزر القناة:")
        
        elif text == "➕ إضافة نص":
            pending[user_id] = "msg"
            await m.reply("📝 أرسل الآن نص الإعلان:")

        # استلام البيانات المكتوبة
        elif user_id in pending:
            mode = pending.pop(user_id)
            if mode == "chat":
                cur.execute("INSERT OR IGNORE INTO targets (id) VALUES (?)", (text,))
                db.commit()
                await m.reply(f"✅ تمت إضافة القناة: {text}")
            elif mode == "msg":
                cur.execute("INSERT INTO messages (content) VALUES (?)", (text,))
                db.commit()
                await m.reply("✅ تم حفظ النص.")