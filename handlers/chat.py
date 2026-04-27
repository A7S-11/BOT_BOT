import google.generativeai as genai
from pyrogram import Client, filters
import os
import asyncio
import random
import logging

log = logging.getLogger(__name__)

# إعداد Gemini - تأكد إن المفتاح بـ Railway اسمه GEMINI_API_KEY
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

def register(app, db, cur):
    @app.on_message(filters.text & filters.private & ~filters.me)
    async def chat_handler(client, m):
        user_id = m.from_user.id
        user_name = m.from_user.first_name or "الغالي"
        text = m.text
        
        log.info(f"📩 رسالة جديدة من {user_name} ({user_id})")

        try:
            # 1. محاكاة القراءة (ثانيتين)
            await client.send_chat_action(m.chat.id, "typing")
            await asyncio.sleep(2)

            # 2. تعليمات الرد "الجامد"
            prompt = f"""
            أنت 'علوش' مبرمج عراقي خبير وقوي. 
            رد على هالكلام بلهجة عراقية بحتة (شعبية وممتعة).
            خليك ذكي، لا ترحب هواي، ادخل بالموضوع كبل. 
            إذا سأل عن بوتات أو برمجة، بين عضلاتك وخبرتك.
            
            اسم المرسل: {user_name}
            كلامه: {text}
            
            ردك العراقي:
            """
            
            response = model.generate_content(prompt)
            
            if response.text:
                # 3. محاكاة الكتابة قبل الإرسال
                await client.send_chat_action(m.chat.id, "typing")
                await asyncio.sleep(1)
                await m.reply(response.text)
                log.info(f"✅ تم الرد على {user_name}")
            else:
                await m.reply("كول عيوني، اسمعك..")
                
        except Exception as e:
            log.error(f"❌ خطأ بالرد: {e}")
            await m.reply("ثواني عيني، النت يمي تعبان.")
