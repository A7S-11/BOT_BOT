import random

STYLES = ["aggressive", "friendly", "expert", "scarcity"]

def choose_style(state):
    if state == "closer":
        return "aggressive"
    elif state == "hot":
        return random.choice(["aggressive", "scarcity"])
    elif state == "warm":
        return random.choice(["friendly", "expert"])
    return "expert"

def get_best_style(cur):
    rows = cur.execute("SELECT style, success, total FROM style_stats").fetchall()
    best = "friendly"
    best_ratio = 0

    for s, suc, tot in rows:
        if tot > 0:
            ratio = suc / tot
            if ratio > best_ratio:
                best_ratio = ratio
                best = s

    return best