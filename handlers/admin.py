from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

pending = {}

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 إدارة النشر", callback_data="p_menu"),
         InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")],
        [InlineKeyboardButton("🧠 شخصية AI", callback_data="ai_menu"),
         InlineKeyboardButton("👥 قائمة العملاء", callback_data="clients_list")],
        [InlineKeyboardButton("⚙️ الإعدادات العامة", callback_data="settings")],
        [InlineKeyboardButton("🧹 تصفير البيانات", callback_data="reset")]
    ])

def register(bot, db, cur, admin_id):
    @bot.on_callback_query(filters.user(admin_id))
    async def cb_handler(_, q: CallbackQuery):
        if q.data == "stats":
            c_count = cur.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
            t_count = cur.execute("SELECT COUNT(*) FROM targets").fetchone()[0]
            await q.answer(f"📊 العملاء: {c_count} | القنوات: {t_count}", show_alert=True)
            
        elif q.data == "clients_list":
            rows = cur.execute("SELECT name, state FROM clients LIMIT 10").fetchall()
            text = "👥 **أحدث العملاء المتفاعلين:**\n\n"
            for r in rows:
                text += f"👤 {r[0]} - الحالة: {r[1]}\n"
            await q.message.edit_text(text, reply_markup=main_menu())
            
        elif q.data == "p_menu":
            # كود قائمة النشر اللي سويناه سابقاً
            pass
