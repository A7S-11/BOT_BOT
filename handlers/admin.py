from pyrogram import filters

def register(app, cur):

    @app.on_message(filters.command("mark_success"))
    async def mark(_, m):
        cur.execute("""
        UPDATE learning_data SET success=1 
        WHERE id=(SELECT id FROM learning_data ORDER BY id DESC LIMIT 1)
        """)
        await m.reply("✅ صفقة ناجحة")