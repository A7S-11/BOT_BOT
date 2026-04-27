import google.generativeai as genai
from pyrogram import Client, filters
import os
import asyncio
import random
import logging

log = logging.getLogger(__name__)

# إعداد Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

def register(app, db, cur):
    # الفلتر هسة يشمل كل الرسائل النصية الخاصة ومن غير حسابك
    @app.on_message(filters.text & filters.private & ~filters.me)
    async def chat_handler(client, m):
        user_id = m.from_user.id
        text = m.text
        
        log.info(f"📩 وصلت رسالة من: {user_id}")

        try:
            # --- ميزة التفكير والانتظار الذكي ---
            # أولاً: يبين إنه "جاري الكتابة" لفترة عشوائية حسب طول الرسالة
            await client.send_chat_action(m.chat.id, "typing")
            wait_time = random.uniform(2, 5) # ينتظر بين 2 إلى 5 ثواني كأنه جاي يقرأ
            await asyncio.sleep(wait_time)

            # --- توجيه الذكاء الاصطناعي (Prompt) ---
            prompt = f"""
            أنت 'علوش' مبرمج وبوت ديفيلوبر عراقي، ذكي وشخصيتك قوية.
            رد بلهجة عراقية شعبية (مو رسمية)، خلي الرد يبين كأنك شخص حقيقي جاي يدردش.
            ممنوع تستخدم كلمات مثل "أهلاً بك" أو "كيف يمكنني مساعدتك".
            إذا سألك عن برمجة أو بوتات، جاوبه كخبير.
            إذا سألك سؤال عادي، رد بذكاء ومزاح عراقي.
            
            الكلام اللي وصلك: {text}
            """
            
            response = model.generate_content(prompt)
            
            if response.text:
                # يرجع يسوي typing قبل الإرسال الفعلي
                await client.send_chat_action(m.chat.id, "typing")
                await asyncio.sleep(1)
                await m.reply(response.text)
                log.info(f"✅ تم الرد بذكاء على {user_id}")
            else:
                await m.reply("ها عيوني، كول شمحتاج؟")
                
        except Exception as e:
            log.error(f"❌ خطأ في الرد الذكي: {e}")
