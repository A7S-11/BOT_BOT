import random

# الأساليب المتاحة للبوت
STYLES = ["aggressive", "friendly", "expert", "scarcity"]

def choose_style(state):
    """يختار الأسلوب الأنسب بناءً على درجة حرارة الزبون"""
    if state == "closer":
        return "aggressive" # إغلاق الصفقة بقوة
    elif state == "hot":
        return random.choice(["aggressive", "scarcity"]) # ضغط الوقت أو الحسم
    elif state == "warm":
        return random.choice(["friendly", "expert"]) # بناء ثقة أو تقديم خبرة
    
    return "friendly" # الافتراضي للزبون الجديد (Cold)

def get_best_style(cur):
    """يجلب أفضل أسلوب حقق نجاحاً من قاعدة البيانات"""
    try:
        # ملاحظة: تأكد أن الجدول موجود، أو استخدم try-except للأمان
        rows = cur.execute("SELECT style, success, total FROM style_stats").fetchall()
        
        if not rows:
            return "friendly" # إذا الجدول فارغ، نرجع للأسلوب الودي كافتراضي

        best = "friendly"
        max_ratio = -1.0

        for s, suc, tot in rows:
            if tot > 0:
                ratio = suc / tot
                if ratio > max_ratio:
                    max_ratio = ratio
                    best = s
        return best

    except Exception as e:
        # إذا الجدول مو موجود أو صار خطأ، نختار عشوائي حتى ما يوقف البوت
        return random.choice(STYLES)
