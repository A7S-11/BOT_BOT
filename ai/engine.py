import google.generativeai as genai
from os import environ

# إعداد المحرك باستخدام المفتاح اللي ضفته بـ Railway
genai.configure(api_key=environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

async def generate_reply(text, state, memory):
    try:
        # تحويل الذاكرة إلى نص مفهوم للـ AI
        history = "\n".join(memory)
        
        prompt = f"""
        أنت 'علوش'، شخص حقيقي ترد بلهجة عراقية محبوبة.
        حالة الشخص: {state}
        تاريخ المحادثة: {history}
        
        السؤال: {text}
        رد بذكاء واختصار:
        """
        
        response = model.generate_content(prompt)
        return response.text if response.text else "هلا بيك عيوني"
    except Exception as e:
        print(f"AI Error: {e}")
        return "ثواني عيوني، النت يقطع يمي.."

async def rewrite_ad(text):
    # ميزة صياغة الإعلانات اللي تطلع بلوحة التحكم
    try:
        prompt = f"أعد صياغة هذا الإعلان بأسلوب جذاب للنشر: {text}"
        response = model.generate_content(prompt)
        return response.text
    except:
        return text
