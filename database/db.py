import sqlite3

def get_db():
    db = sqlite3.connect("data.db", check_same_thread=False)
    cur = db.cursor()

    # 📢 القنوات
    cur.execute("""
    CREATE TABLE IF NOT EXISTS targets (
        id TEXT
    )
    """)

    # 📝 النصوص
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        content TEXT
    )
    """)

    # 👥 العملاء
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        user_id INTEGER PRIMARY KEY,
        score INTEGER,
        state TEXT
    )
    """)

    # 🧠 التعلم
    cur.execute("""
    CREATE TABLE IF NOT EXISTS learning_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_text TEXT,
        bot_reply TEXT,
        state TEXT,
        style TEXT,
        success INTEGER DEFAULT 0
    )
    """)

    # ⚙️ إعدادات
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    db.commit()
    return db, cur