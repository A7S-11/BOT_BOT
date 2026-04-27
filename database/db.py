import sqlite3

def get_db():
    db = sqlite3.connect("data.db", check_same_thread=False)
    cur = db.cursor()

    # ───── targets ─────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS targets (
        id TEXT PRIMARY KEY
    )
    """)

    # ───── messages ─────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT
    )
    """)

    # ───── clients ─────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        user_id INTEGER PRIMARY KEY,
        score INTEGER DEFAULT 0,
        state TEXT DEFAULT 'cold'
    )
    """)

    # ───── learning_data ─────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS learning_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_text TEXT,
        bot_reply TEXT,
        state TEXT,
        style TEXT,
        success INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ───── settings ─────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # ───── تحديث schema (حل مشاكل قديمة) ─────
    fix_schema(cur)

    db.commit()
    return db, cur


# ───── FIX SCHEMA ─────
def fix_schema(cur):

    # إضافة عمود success إذا ما موجود
    try:
        cur.execute("ALTER TABLE learning_data ADD COLUMN success INTEGER DEFAULT 0")
    except:
        pass

    # إضافة created_at
    try:
        cur.execute("ALTER TABLE learning_data ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    except:
        pass

    # إضافة score/state إذا ناقصين
    try:
        cur.execute("ALTER TABLE clients ADD COLUMN score INTEGER DEFAULT 0")
    except:
        pass

    try:
        cur.execute("ALTER TABLE clients ADD COLUMN state TEXT DEFAULT 'cold'")
    except:
        pass