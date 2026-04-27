import asyncio
import logging
import random
from ai.engine import generate_reply

log = logging.getLogger(__name__)

async def retarget(bot, cur):
    log.info("🎯 Retargeting engine started...")
    
    while True:
        try:
            # جلب المستخدمين اللي حالتهم (warm أو hot) 
            # ملاحظة: يفضل إضافة عمود last_retarget في قاعدة البيانات لتجنب الإزعاج
            rows = cur.execute(
                "SELECT user_id, state FROM clients WHERE state IN ('warm', 'hot')"
            ).fetchall()

            for user_id, state in rows:
                try:
                    # احتمالية بسيطة للإرسال حتى لا يرسل للكل بنفس الوقت (تمويه)
                    if random.random() > 0.3: 
                        continue

                    # تجهيز رسالة ذكية بدل الرسائل الثابتة
                    prompt_text = "سوي إعادة استهداف لهذا الزبون بكلمتين سريعة وبدون إزعاج"
                    
                    # نستخدم الـ AI لتوليد رسالة خفيفة
                    # ملاحظة: مررنا قائمة فارغة للميموري هنا للاختصار
                    smart_msg = await generate_reply(
                        text=prompt_text,
                        state=state,
                        style="scarcity" if state == "hot" else "friendly",
                        best_style="friendly",
                        memory=[],
                        cur=cur
                    )

                    await bot.send_message(user_id, smart_msg)
                    log.info(f"✨ Retargeted user {user_id} with state: {state}")
                    
                    # تأخير بين مستخدم ومستخدم حتى لا يعتبرنا تليجرام سبام
                    await asyncio.sleep(random.randint(5, 15))

                except Exception as e:
                    log.error(f"❌ Failed to retarget {user_id}: {e}")
                    continue

        except Exception as e:
            log.error(f"🔥 Retargeting main loop error: {e}")

        # استراحة طويلة (مثلاً كل 4 ساعات) حتى لا يكون البوت مزعجاً
        # 14400 ثانية = 4 ساعات
        log.info("💤 Retargeting cycle finished. Sleeping for 4 hours...")
        await asyncio.sleep(14400)
