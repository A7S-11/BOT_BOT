def calculate_score(text):
    score = 0
    text = text.lower() # تحويل النص لأسفل لضمان المطابقة
    
    # قائمة الكلمات المفتاحية مع وزن كل وحدة
    keywords = {
        "اريد": 7, "أريد": 7, "اريد اشترك": 10, "محتاج": 5, "ابحث": 5, # نية شراء قوية
        "كم": 5, "بكم": 5, "سعر": 5, "بيش": 5, "قديش": 5,            # استفسار عن السعر
        "تفاصيل": 3, "شرح": 3, "معلومات": 3,                        # استفسار عام
        "شلون": 3, "كيف": 3, "طريقة": 3,                            # استفسار عن الطريقة
        "رقمك": 8, "واتساب": 8, "تواصل": 8                         # نية إغلاق (Closer)
    }

    for word, points in keywords.items():
        if word in text:
            score += points
            
    return score

def get_state(score):
    # الحالات بناءً على النقاط التراكمية
    if score >= 20: return "closer" # رفعت الدرجة قليلاً لضمان التأكد
    if score >= 12: return "hot"
    if score >= 5:  return "warm"
    return "cold"
