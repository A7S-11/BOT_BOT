import asyncio
import random
from ai.engine import rewrite_ad

async def publisher(app, cur):
    while True:
        targets = [x[0] for x in cur.execute("SELECT id FROM targets")]
        msgs = [x[0] for x in cur.execute("SELECT content FROM messages")]

        random.shuffle(targets)

        for t in targets:
            msg = await rewrite_ad(random.choice(msgs))
            await app.send_message(int(t), msg)
            await asyncio.sleep(random.randint(60, 120))