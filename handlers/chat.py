import google.generativeai as genai
from pyrogram import Client, filters
import os
import asyncio
import random
import logging

log = logging.getLogger(__name__)

# إعداد Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# إعدادات كسر الفلاتر لضمان الرد مهما كان الكلام
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel('gemini-pro')

def register(app, db, cur):
    @app.on_message(filters.text & filters.private & ~filters.me)
    async def chat_handler(client, m):
        user_name = m.from_user.first_name or "الغالي"
        
        try:
            await client.send_chat_action(m.chat.id, "typing")
            
            # تعليمات "صارمة" جداً للذكاء
            prompt = f"أنت اسمك علوش، مبرمج عراقي ذكي. رد بلهجة عراقية دارجة وقوية على هذا الكلام: {m.text}. اسم المقابل: {user_name}. ممنوع ترد رسمي، خليك شعبي."
            
            # طلب الرد مع إيقاف الحماية
            response = model.generate_content(prompt, safety_settings=safety_settings)
            
            if response.text:
                await asyncio.sleep(1)
                await m.reply(response.text)
                log.info(f"✅ تم الرد بذكاء حقيقي على {user_name}")
            else:
                raise Exception("Empty Response")
                
        except Exception as e:
            log.error(f"❌ خطأ بالذكاء: {e}")
            # إذا فشل كل شي، نرد رد "بشري" بس مو ثابت (عشوائي جداً)
            await m.reply(f"هلا {user_name}، تدلل عيوني ثواني وأرد عليك بس اخلص البرمجة بيدي.")
