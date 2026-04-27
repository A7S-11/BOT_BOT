import google.generativeai as genai
from pyrogram import filters
import os
import asyncio
import logging

log = logging.getLogger(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-1.5-pro')

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

            prompt = (
                f"أنت مبرمج عراقي اسمك علوش، تحچي باللهجة البغدادية. "
                f"رد على: {m.text} "
                f"بأسلوب طبيعي ومرح بدون فصحى."
            )

            response = model.generate_content(prompt, safety_settings=safety_settings)

            text = getattr(response, "text", None)

            if text:
                await asyncio.sleep(1)
                await m.reply(text)
                log.info("✅ رد ناجح")
            else:
                alt = model.generate_content(f"جاوب بطريقة ذكية: {m.text}")
                await m.reply(getattr(alt, "text", "ماكدر أرد هسه 😅"))

        except Exception as e:
            log.error(f"❌ خطأ بالذكاء: {e}")