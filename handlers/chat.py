import google.generativeai as genai
from pyrogram import Client, filters
import os
import asyncio
import logging

log = logging.getLogger(__name__)

# إعداد Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# تحديث اسم الموديل للنسخة الجديدة والمستقرة
model = genai.GenerativeModel('gemini-1.5-flash')

# إعدادات كسر الفلاتر لضمان الرد الشعبي
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
            
            # محاولة الرد العراقي الذكي
            prompt_iraqi = (
                f"أنت علوش مبرمج عراقي، رد بلهجة عراقية دارجة وقوية "
                f"على: '{m.text}'. اسم المرسل: {user_name}."
            )
            
            response = model.generate_content(prompt_iraqi, safety_settings=safety_settings)
            
            if response and response.text:
                await asyncio.sleep(1)
                await m.reply(response.text)
                log.info(f"✅ تم الرد بالعراقي المحدث على {user_name}")
            else:
                raise Exception("فشل توليد النص")

        except Exception as e:
            log.warning(f"⚠️ فشل العراقي، جاري محاولة الفصحى: {e}")
            try:
                # محاولة الفصحى الرسمية كخطة بديلة
                prompt_formal = f"أجب بذكاء وباللغة العربية الفصحى على: {m.text}"
                response_formal = model.generate_content(prompt_formal)
                if response_formal.text:
                    await m.reply(response_formal.text)
            except Exception as e2:
                log.error(f"❌ فشل كلي: {e2}")
