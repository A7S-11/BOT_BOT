import google.generativeai as genai
from pyrogram import Client, filters
import os
import asyncio
import logging

log = logging.getLogger(__name__)

# إعداد Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# إعدادات كسر الفلاتر لضمان أعلى استجابة
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
            
            # المحاولة الأولى: رد عراقي شعبي (علوش المبرمج)
            prompt_iraqi = (
                f"أنت مبرمج عراقي اسمك علوش. رد بلهجة عراقية دارجة "
                f"على: '{m.text}'. اسم الشخص: {user_name}. "
                f"خليك طبيعي ومرح."
            )
            
            response = model.generate_content(prompt_iraqi, safety_settings=safety_settings)
            
            if response and response.text:
                await asyncio.sleep(1)
                await m.reply(response.text)
                log.info(f"✅ تم الرد بالعراقي على {user_name}")
            else:
                raise Exception("فشل في توليد اللهجة")

        except Exception as e:
            log.warning(f"⚠️ تحويل للفصحى بسبب: {e}")
            try:
                # المحاولة الثانية (الخطة البديلة): لغة عربية رسمية وذكية
                prompt_formal = (
                    f"أجب كخبير تقني بلغة عربية فصحى مهذبة ومختصرة "
                    f"على رسالة المستخدم: '{m.text}'. "
                    f"المستخدم يدعى: {user_name}."
                )
                response_formal = model.generate_content(prompt_formal)
                
                if response_formal and response_formal.text:
                    await m.reply(response_formal.text)
                    log.info(f"✅ تم الرد بالفصحى على {user_name}")
            except Exception as e2:
                log.error(f"❌ فشل كلي في الذكاء: {e2}")

