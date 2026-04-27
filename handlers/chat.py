import asyncio
import logging
import google.generativeai as genai
from pyrogram import filters
from config import GEMINI_API_KEY

log = logging.getLogger(__name__)

# إعداد Gemini
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash-latest")

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# دالة استخراج النص بدون أخطاء
def extract_text(response):
    try:
        if hasattr(response, "text") and response.text:
            return response.text
    except:
        pass

    try:
        return response.candidates[0].content.parts[0].text
    except:
        pass

    return str(response)

def register(app):
    @app.on_message(filters.text & filters.private & ~filters.me)
    async def chat_handler(client, m):
        user_name = m.from_user.first_name or "حبي"

        try:
            await client.send_chat_action(m.chat.id, "typing")

            prompt = (
                f"أنت مبرمج عراقي اسمك علوش، تحچي باللهجة البغدادية. "
                f"رد على {user_name} اللي كالك: {m.text} "
                f"بأسلوب ذكي ومرح بدون فصحى."
            )

            response = model.generate_content(
                prompt,
                safety_settings=safety_settings
            )

            text = extract_text(response)

            if text:
                await asyncio.sleep(1)
                await m.reply(text)
                log.info("✅ رد ناجح")
            else:
                await m.reply("ماكدر أرد هسه 😅")

        except Exception as e:
            log.error(f"❌ خطأ AI: {e}")
            await m.reply("صار خطأ بسيط 😅")