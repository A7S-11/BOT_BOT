from openai import AsyncOpenAI
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ───── جلب إعداد AI من DB ─────
def get_ai_style(cur, default_style):
    try:
        row = cur.execute(
            "SELECT value FROM settings WHERE key='ai_style'"
        ).fetchone()

        if row and row[0]:
            return row[0]
    except:
        pass

    return default_style


# ───── توليد رد ذكي ─────
async def generate_reply(text, state, style, best_style, memory, cur):

    # جلب الأسلوب المختار من لوحة التحكم
    selected_style = get_ai_style(cur, style)

    # تحويل الأسلوب إلى وصف
    style_map = {
        "friendly": "ودي، خفيف، يحسس المستخدم بالراحة",
        "aggressive": "مباشر، يدفع للشراء بسرعة",
        "expert": "احترافي، يشرح ويعطي ثقة",
        "scarcity": "يحسس المستخدم أن الفرصة محدودة"
    }

    style_desc = style_map.get(selected_style, "ودي")

    # تحويل الحالة
    state_desc = {
        "cold": "المستخدم جديد، لا تضغط عليه",
        "warm": "المستخدم مهتم، حاول تقنعه",
        "hot": "المستخدم قريب يشتري، ادفعه",
        "closer": "المستخدم جاهز، اغلق الصفقة"
    }

    # تجهيز الذاكرة
    memory_text = "\n".join(memory[-5:]) if memory else ""

    # ───── البرومبت الذكي ─────
    prompt = f"""
انت بائع عراقي محترف.

📌 حالياً:
- حالة المستخدم: {state} ({state_desc.get(state)})
- أسلوبك: {selected_style} ({style_desc})
- أفضل أسلوب سابق: {best_style}

📊 المحادثة السابقة:
{memory_text}

🎯 المطلوب:
- رد باللهجة العراقية
- لا تكرر كلامك
- لا تعطي السعر مباشرة إلا إذا طلبه بوضوح
- حاول تقنع المستخدم
- استخدم أسلوبك بذكاء
- إذا المستخدم جاهز → اغلق الصفقة
"""

    try:
        res = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.8
        )

        return res.choices[0].message.content.strip()

    except Exception as e:
        print("AI ERROR:", e)
        return "صار خطأ بسيط، اكتبلي مرة ثانية 🙏"


# ───── إعادة كتابة إعلان ─────
async def rewrite_ad(text):

    prompt = f"""
أعد كتابة هذا الإعلان باللهجة العراقية بأسلوب جذاب:

{text}

الشروط:
- خلي الكلام مختلف
- قصير
- يجذب الانتباه
- مناسب للنشر بالكروبات
"""

    try:
        res = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "كاتب إعلانات محترف"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9
        )

        return res.choices[0].message.content.strip()

    except Exception as e:
        print("Rewrite Error:", e)
        return text


# ───── توليد عدة نسخ إعلان (Smart Publish) ─────
async def generate_ad_variants(text, count=3):
    variants = []

    for _ in range(count):
        v = await rewrite_ad(text)
        variants.append(v)

    return variants