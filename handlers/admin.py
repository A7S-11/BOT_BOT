 from pyrogram import filters
from pyrogram.types import ReplyKeyboardMarkup, Message
import logging

log = logging.getLogger(__name__)

# آيديك المباشر من Railway
MY_ID = 8780640152 

pending = {}

def main_menu():
    return ReplyKeyboardMarkup([
        ["📢 إدارة النشر", "📊 الإحصائيات"],
        ["🧠 شخصية AI", "👥 قائمة العملاء"]
    ], resize_keyboard=True)

def publish_menu():
    return ReplyKeyboardMarkup([
        ["➕ إضافة قناة", "➕ إضافة نص"],
        ["📋 عرض القنوات", "🔙 رجوع"]
    ], resize_keyboard=True)

def register(bot, db, cur, admin_id):
    # استخدمنا MY_ID مباشرة بدل admin_id لضمان العمل
    @bot.on_message(filters.command("start") & filters.user(MY_ID))
    async def start_cmd(_, m: Message):
        await m.reply("أهلاً علوش، تم تفعيل الأزرار بنجاح ✅", reply_markup=main_menu())

    @bot.on_message(filters.text & filters.user(MY_ID))
    async def handle_logic(_, m: Message):
        text = m.text
        uid = m.from_user.id

        if text == "📢 إدارة النشر":
            await m.reply("قائمة إدارة النشر التلقائي:", reply_markup=publish_menu())
        elif text == "🔙 رجوع":
            await m.reply("القائمة الرئيسية:", reply_markup=main_menu())
        elif text == "➕ إضافة قناة":
            pending[uid] = "chat"
            await m.reply("📌 أرسل يوزر القناة الآن:")
        elif uid in pending:
            mode = pending.pop(uid)
            if mode == "chat":
                cur.execute("INSERT OR IGNORE INTO targets (id) VALUES (?)", (text,))
                db.commit()
                await m.reply(f"✅ تمت إضافة: {text}")
