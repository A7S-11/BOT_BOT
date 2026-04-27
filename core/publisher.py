import asyncio
import random
import logging
from pyrogram.errors import FloodWait
from ai.engine import rewrite_ad

log = logging.getLogger(__name__)

async def publisher(app, cur):

    while True:
        try:
            targets = [x[0] for x in cur.execute("SELECT id FROM targets").fetchall()]
            msgs = [x[0] for x in cur.execute("SELECT content FROM messages").fetchall()]

            if not targets:
                log.warning("⚠️ ماكو قنوات")
                await asyncio.sleep(30)
                continue

            if not msgs:
                log.warning("⚠️ ماكو نصوص")
                await asyncio.sleep(30)
                continue

            random.shuffle(targets)

            # توليد نسخة إعلان واحدة لكل دورة (مو لكل قناة)
            base_msg = random.choice(msgs)
            try:
                smart_msg = await rewrite_ad(base_msg)
            except:
                smart_msg = base_msg

            for t in targets:
                try:
                    await app.send_message(int(t), smart_msg)
                    log.info(f"✅ تم النشر في {t}")

                except FloodWait as e:
                    log.warning(f"⏳ FloodWait {e.value}s")
                    await asyncio.sleep(e.value)

                except Exception as e:
                    log.error(f"❌ فشل في {t}: {e}")

                # Delay عشوائي (Anti-ban)
                await asyncio.sleep(random.randint(60, 120))

        except Exception as e:
            log.error(f"🔥 خطأ عام في publisher: {e}")

        # استراحة بين الجولات
        await asyncio.sleep(10)