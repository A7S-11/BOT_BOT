import asyncio
import random
import logging
from pyrogram.errors import FloodWait, RPCError
from ai.engine import rewrite_ad

log = logging.getLogger(__name__)

async def publisher(app, cur):
    log.info("🚀 Publisher task started...")

    while True:
        try:
            # جلب الأهداف والنصوص
            targets = [x[0] for x in cur.execute("SELECT id FROM targets").fetchall()]
            msgs = [x[0] for x in cur.execute("SELECT content FROM messages").fetchall()]

            if not targets:
                log.warning("⚠️ قائمة الأهداف (targets) فارغة. سأنتظر 60 ثانية...")
                await asyncio.sleep(60)
                continue

            if not msgs:
                log.warning("⚠️ قائمة الرسائل (messages) فارغة.")
                await asyncio.sleep(60)
                continue

            # خلط القنوات لكسر النمط التكراري
            random.shuffle(targets)
            
            # اختيار نص أساسي للدورة
            base_msg = random.choice(msgs)
            
            # متغير لحفظ النص المطور (تحديثه كل فترة)
            current_smart_msg = None

            for index, t in enumerate(targets):
                try:
                    # تحديث نص الإعلان كل 3 قنوات لزيادة التمويه (Anti-Spam)
                    if index % 3 == 0 or current_smart_msg is None:
                        try:
                            current_smart_msg = await rewrite_ad(base_msg)
                            log.info("🔄 Generated a new variant of the ad.")
                        except:
                            current_smart_msg = base_msg

                    # التعامل مع الـ ID سواء كان رقم أو يوزرنيم
                    target_id = int(t) if str(t).replace('-', '').isdigit() else str(t)
                    
                    await app.send_message(target_id, current_smart_msg)
                    log.info(f"✅ تم النشر بنجاح في: {target_id}")

                    # Delay عشوائي بين قناة وقناة (ضروري جداً)
                    wait_time = random.randint(60, 180) # زيادة الوقت قليلاً للأمان
                    await asyncio.sleep(wait_time)

                except FloodWait as e:
                    log.warning(f"⏳ حظر مؤقت (FloodWait): نحتاج للانتظار {e.value} ثانية.")
                    await asyncio.sleep(e.value + 5) # إضافة 5 ثواني أمان

                except RPCError as e:
                    log.error(f"❌ خطأ من تليجرام في {t}: {e.MESSAGE}")
                    continue # تخطي هذه القناة

                except Exception as e:
                    log.error(f"❌ خطأ غير متوقع في {t}: {e}")
                    continue

        except Exception as e:
            log.error(f"🔥 خطأ عام في محرك الناشر: {e}")
            await asyncio.sleep(30)

        # استراحة بين جولة وجولة (مثلاً كل ساعة)
        log.info("💤 انتهت الجولة. استراحة لمدة 10 دقائق قبل البدء من جديد.")
        await asyncio.sleep(600) 
