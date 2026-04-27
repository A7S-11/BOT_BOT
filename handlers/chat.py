import google.generativeai as genai
from pyrogram import Client, filters
import os
import asyncio
import logging

log = logging.getLogger(__name__)

# إعداد Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# إعدادات صارمة لكسر فلاتر المحتوى - حتى يجاوب بكل حرية
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
            # إظهار حالة جاري الكتابة
            await client.send_chat_action(m.chat.id, "typing")
            
            # برومبت (تعليمات) مكثفة تجبره على التفكير والرد العراقي
            prompt = (
                f"أنت 'علوش' مبرمج عراقي حقيقي، لسانك عراقي شعبي بحت. "
                f"رد بذكاء وفطنة على: '{m.text}'. "
                f"ملاحظة: المقابل اسمه {user_name}. "
                f"ردك لازم يكون عراقي 100% وممنوع ترد بأي لغة ثانية أو بأسلوب رسمي. "
                f"انطلق!"
            )
            
            # طلب التوليد من الذكاء فقط
            response = model.generate_content(prompt, safety_settings=safety_settings)
            
            if response.text:
                # تأخير بسيط جداً حتى يبين إنه فكر قبل الرد
                await asyncio.sleep(1.5)
                await m.reply(response.text)
                log.info(f"✅ رد ذكي من Gemini على: {user_name}")
            else:
                log.warning("⚠️ الذكاء لم يرجع نصاً (ممكن مشكلة فلاتر)")
                
        except Exception as e:
            # هنا ما راح ندز "رد جاهز"، بس نطبع الخطأ باللوكات حتى نصلحه
            log.error(f"❌ خطأ حقيقي في محرك الذكاء: {e}")
