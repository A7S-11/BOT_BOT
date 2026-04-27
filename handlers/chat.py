import google.generativeai as genai
from pyrogram import Client, filters
import os
import asyncio
import logging

log = logging.getLogger(__name__)

# إعداد Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# استخدم Flash حصراً لأنه أسرع وأفضل للهجة
model = genai.GenerativeModel('gemini-1.5-flash')

# إعدادات لفتح كل القيود (BLOCK_NONE)
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
            
            # برومبت (تعليمات) تجبره يترك الرسميات
            prompt = (
                f"اسمك علوش، مبرمج عراقي. رد بلهجة عراقية شعبية قوية "
                f"على هذا الكلام: '{m.text}'. "
                f"ممنوع ترد لغة عربية فصحى نهائياً. انطلق باللهجة العراقية فقط!"
            )
            
            response = model.generate_content(prompt, safety_settings=safety_settings)
            
            # التأكد من استلام النص بشكل صحيح
            if response and response.text:
                await asyncio.sleep(1)
                await m.reply(response.text)
                log.info(f"✅ تم الرد بذكاء عراقي على {user_name}")
            else:
                # إذا فشل العراقي، نجرب نطلب منه رد "ذكي" بالفصحى بدون ما ندز رد ثابت
                log.warning("⚠️ محاولة توليد رد فصيح كبديل...")
                alt_res = model.generate_content(f"رد بذكاء كخبير تقني على: {m.text}")
                await m.reply(alt_res.text)

        except Exception as e:
            log.error(f"❌ خطأ بالذكاء: {e}")
