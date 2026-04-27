import google.generativeai as genai
from pyrogram import Client, filters
import os
import asyncio
import logging

log = logging.getLogger(__name__)

# إعداد Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# الموديل الصحيح والشغال حالياً هو 1.5 فلاش
model = genai.GenerativeModel('gemini-1.5-flash')

# إعدادات الأمان لفتح قفل اللهجة العراقية
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

def register(app, db, cur):
    @app.on_message(filters.text & filters.private & ~filters.me)
    async def chat_handler(client, m):
        user_name = m.from_user.first_name or "الغالي"
        
        try:
            await client.send_chat_action(m.chat.id, "typing")
            
            # تعليمات واضحة للموديل
            prompt = (
                f"أنت علوش، مبرمج عراقي ذكي. "
                f"رد بلهجة عراقية شعبية قوية على: '{m.text}'. "
                f"اسم المقابل: {user_name}. "
                f"ممنوع ترد رسمي، خلي ردك ذكي ويسولف وياه."
            )
            
            # طلب التوليد
            response = model.generate_content(prompt, safety_settings=safety_settings)
            
            if response and response.text:
                await asyncio.sleep(1) # حتى يبين حقيقي
                await m.reply(response.text)
                log.info(f"✅ تم الرد بذكاء (عراقي) على {user_name}")
            else:
                raise Exception("Empty text from AI")

        except Exception as e:
            log.error(f"❌ خطأ بالذكاء: {e}")
            # إذا فشل العراقي، نجرب فصحى بس بذكاء (بدون رد جاهز)
            try:
                formal_res = model.generate_content(f"رد بذكاء وباللغة العربية على: {m.text}")
                if formal_res.text:
                    await m.reply(formal_res.text)
            except:
                pass
