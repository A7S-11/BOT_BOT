import google.generativeai as genai
from os import environ

# إعداد مفتاح API
genai.configure(api_key=environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

async def generate_reply(text, state, memory):
    try:
        # بناء التعليمات للبوت
        prompt = f"""
        أنت 'علوش'، شخص حقيقي ذكي ترد بلهجة عراقية محبوبة.
        حالة الشخص اللي تراسله: {state}
        سياق المحادثة السابقة: {memory}
        
        هو قال: {text}
        رد عليه بذكاء واختصار:
        """
        response = model.generate_content(prompt)
        return response.text if response.text else "هلا بيك عيوني"
    except Exception as e:
        print(f"AI Engine Error: {e}")
        return "ثواني عيوني، النت يقطع يمي.."

async def rewrite_ad(text):
    # ميزة إعادة صياغة الإعلانات للنشر التلقائي
    try:
        prompt = f"أعد صياغة هذا الإعلان بأسلوب جذاب للنشر في القنوات: {text}"
        response = model.generate_content(prompt)
        return response.text
    except:
        return text
