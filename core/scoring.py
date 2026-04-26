def calculate_score(text):
    score = 0
    if "اريد" in text: score += 7
    if "كم" in text: score += 5
    if "تفاصيل" in text: score += 2
    if "شلون" in text: score += 3
    return score

def get_state(score):
    if score >= 15: return "closer"
    if score >= 10: return "hot"
    if score >= 5: return "warm"
    return "cold"