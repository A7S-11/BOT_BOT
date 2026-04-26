import asyncio

async def retarget(bot, cur):
    while True:
        rows = cur.execute("SELECT user_id, state FROM clients").fetchall()

        for user_id, state in rows:
            if state == "warm":
                await bot.send_message(user_id, "🔥 بعدك مهتم؟")
            elif state == "hot":
                await bot.send_message(user_id, "خل نغلقها اليوم 👌")

        await asyncio.sleep(1800)