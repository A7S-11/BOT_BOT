from openai import AsyncOpenAI
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_reply(text, state, style, best_style, memory):

    prompt = f"""
انت بائع محترف.

الأسلوب الحالي: {style}
أفضل أسلوب: {best_style}

المحادثة:
{memory}

تكلم باللهجة العراقية
لا تعطي السعر مباشرة
هدفك: إقناع المستخدم
"""

    res = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ]
    )

    return res.choices[0].message.content.strip()


async def rewrite_ad(text):
    res = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "اكتب اعلان عراقي جذاب مختلف"},
            {"role": "user", "content": text}
        ]
    )
    return res.choices[0].message.content.strip()