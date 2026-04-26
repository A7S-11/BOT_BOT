from pyrogram import filters
from core.learning import mark_last_success

def register(bot, cur, db):

    # تسجيل صفقة ناجحة
    @bot.on_message(filters.command("mark_success"))
    async def mark(_, m):
        ok = mark_last_success(cur)

        if ok:
            db.commit()
            await m.reply("✅ تم تسجيل صفقة ناجحة + تعلم البوت")
        else:
            await m.reply("❌ ماكو بيانات حتى تنحسب صفقة")

    # عرض أفضل الأساليب
    @bot.on_message(filters.command("styles"))
    async def styles(_, m):
        rows = cur.execute(
            "SELECT style, success, total FROM style_stats"
        ).fetchall()

        if not rows:
            await m.reply("❌ ماكو بيانات بعد")
            return

        text = "📊 أداء الأساليب:\n\n"

        for s, suc, tot in rows:
            ratio = (suc / tot * 100) if tot > 0 else 0
            text += f"{s} → {ratio:.1f}% ({suc}/{tot})\n"

        await m.reply(text)

    # عرض العملاء
    @bot.on_message(filters.command("clients"))
    async def clients(_, m):
        rows = cur.execute(
            "SELECT user_id, score, state FROM clients ORDER BY score DESC LIMIT 10"
        ).fetchall()

        if not rows:
            await m.reply("❌ ماكو عملاء")
            return

        text = "👥 أفضل العملاء:\n\n"

        for u, s, st in rows:
            text += f"{u} | {st} | {s}\n"

        await m.reply(text)