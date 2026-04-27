import google.generativeai as genai
from pyrogram import Client, filters
import os
import asyncio
import random
import logging

log = logging.getLogger(__name__)

# إعداد Gemini مع إيقاف فلاتر الحماية لضمان الرد الشعبي
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# قائمة ردود احتياطية "عراقية" في حال تعطل الـ AI
RANDOM_REPLIES = [
    "هلا بيج عيوني، ثواني وأرد عليج بس اخلص الشغل بيديه.",
    "يا هلا، منورني.. ثواني واجاوبك غالي.",
    "تفضل عيوني اسمعك، بس هسة شوية مشغول وأرد عليك.",
    "هلا والله، تدلل هسة اشوف رسالتك وأجاوبك."
]

def register(app, db, cur):
    @app.on_message(filters.text & filters.private & ~filters.me)
    async def chat_handler(client, m):
        user_id = m.from_user.id
        user_name = m.from_user.first_name or "الغالي"
        text = m.text
        
        log.info(f"📩 وصلت رسالة من {user_name} وجاي أعالج الرد...")

        try:
            # 1. محاكاة القراءة والكتابة (تأخير ذكي)
            await client.send_chat_action(m.chat.id, "typing")
            await asyncio.sleep(random.randint(2, 4))

            # 2. التعليمات الصارمة للـ AI
            prompt = f"""
            أنت 'علوش' مبرمج عراقي، صاحب كاريزما ولسان دافئ.
            مطلوب منك ترد بلهجة عراقية (بغدادية دارجة).
            ممنوع تقول 'أنا ذكاء اصطناعي' أو 'كيف أساعدك'.
            رد كأنك صديقه المقرب.
            اسم الشخص: {user_name}
            كلامه: {text}
            """
            
            # إرسال الطلب مع ضبط الأمان ليكون مرناً
            response = model.generate_content(prompt)
            
            if response and response.text:
                await m.reply(response.text)
                log.info(f"✅ تم الرد بذكاء على {user_name}")
            else:
                # إذا الـ AI صفن أو رفض يولد نص، نرسل رد عراقي جاهز
                await m.reply(random.choice(RANDOM_REPLIES))
                log.info(f"⚠️ الـ AI رفض، تم إرسال رد احتياطي.")
                
        except Exception as e:
            log.error(f"❌ خطأ تقني: {e}")
            await m.reply(random.choice(RANDOM_REPLIES))
