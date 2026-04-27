import google.generativeai as genai
from pyrogram import Client, filters
import os
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
        
        log.info(f"📩 وصلت رسالة من: {user_id} - النص: {text}")

        try:
            # إرسال حالة "جاري الكتابة" حتى يبين طبيعي
            await client.send_chat_action(m.chat.id, "typing")

            # تعليمات الذكاء الاصطناعي
            prompt = f"أنت شخص عراقي اسمك علوش، رد بلهجة عراقية شعبية ممتعة على هذا الكلام: {text}"
            
            response = model.generate_content(prompt)
            
            if response.text:
                await m.reply(response.text)
                log.info(f"✅ تم الرد على {user_id}")
            else:
                await m.reply("هلا بيك عيوني..")
                
        except Exception as e:
            log.error(f"❌ خطأ في الرد الذكي: {e}")
            # رد احتياطي في حال فشل الـ AI
            await m.reply("هلا بيك غالي، ثواني وأرد عليك.")
