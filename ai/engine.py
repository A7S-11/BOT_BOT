import asyncio
import os
from openai import AsyncOpenAI

# تعريف الكلاينت مع التأكد من وجود المفتاح
api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)

# ───── جلب إعداد AI من DB ─────
def get_ai_style(cur, default_style):
    try:
        # تأكد من تمرير الـ Cursor بشكل صحيح
        row = cur.execute(
            "SELECT value FROM settings WHERE key='ai_style'"
        ).fetchone()

        if row and row[0]:
            return row[0]
    except Exception as e:
        print(f"DB Error in get_ai_style: {e}")
    
    return default_style

# ───── توليد رد ذكي ─────
async def generate_reply(text, state, style, best_style, memory, cur):

    # جلب الأسلوب المختار
    selected_style = get_ai_style(cur, style)

    style_map = {
        "friendly": "ودي، خفيف، يحسس المستخدم بالراحة",
        "aggressive": "مباشر، يدفع للشراء بسرعة وقوي بالكلام",
        "expert": "احترافي، يشرح ويعطي ثقة، يستخدم مصطلحات تقنية",
        "scarcity": "يحسس المستخدم أن الفرصة محدودة والقطع باقية قليلة"
    }

    state_desc_map = {
        "cold": "المستخدم جديد، لا تضغط عليه، بس انطي فكرة",
        "warm": "المستخدم مهتم، حاول تقنعه وتجاوب أسئلته",
        "hot": "المستخدم قريب يشتري، ادفعه برقة نحو القرار",
        "closer": "المستخدم جاهز، اغلق الصفقة وخذ المعلومات"
    }

    style_desc = style_map.get(selected_style, "ودي")
    state_desc = state_desc_map.get(state, "المستخدم جديد")

    # تجهيز الذاكرة (آخر 5 رسائل)
    memory_text = "\n".join(memory) if memory else "لا يوجد محادثة سابقة"

    prompt = f"""
أنت (بائع عراقي محترف) ذكي وشاطر بالإقناع.

📌 سياق العملية حالياً:
- حالة المستخدم: {state} ({state_desc})
- أسلوبك الحالي: {selected_style} ({style_desc})
- أسلوب نجح سابقاً: {best_style if best_style else 'غير محدد'}

📊 سجل المحادثة (للسياق):
{memory_text}

🎯 تعليمات الرد:
1. الرد حصراً باللهجة العراقية (بغدادية بيضاء مفهومة).
2. لا تكرر نفس الجمل السابقة.
3. لا تعطي السعر مباشرة إلا إذا سأل المستخدم.
4. استخدم "عيوني، غالي، تدلل، ع راسي" بأسلوب الباعة العراقيين.
5. إذا المستخدم "closer" أو "hot" → ركز على إنهاء البيعة (مثلاً اطلب منه الرقم أو العنوان).
"""

    try:
        res = await client.chat.completions.create(
            model="gpt-4o-mini", # خيار ممتاز وسريع لـ Railway
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.8
        )
        return res.choices[0].message.content.strip()

    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return "ثواني عيني، النت يمي تعبان.. ارجع اكتبلي فدوة."

# ───── إعادة كتابة إعلان ─────
async def rewrite_ad(text):
    # نستخدم نفس المنطق العراقي الجذاب
    prompt = f"أعد كتابة هذا الإعلان باللهجة العراقية بأسلوب تسويقي جذاب وقصير ومناسب للكروبات:\n\n{text}"
    
    try:
        res = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "أنت خبير تسويق عراقي (Copywriter)"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9
        )
        return res.choices[0].message.content.strip()
    except:
        return text

# ───── توليد عدة نسخ إعلان (Smart Publish) ─────
async def generate_ad_variants(text, count=3):
    # استخدام gather لتسريع العملية (يطلبهم كلهم بنفس الوقت)
    tasks = [rewrite_ad(text) for _ in range(count)]
    variants = await asyncio.gather(*tasks)
    return variants
