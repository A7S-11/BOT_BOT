import sqlite3

def get_db():
    db = sqlite3.connect("data.db", check_same_thread=False)
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS targets (id TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS messages (content TEXT)")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        user_id INTEGER PRIMARY KEY,
        score INTEGER,
        state TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS learning_data (
        id INTEGER PRIMARY KEY,
        user_text TEXT,
        bot_reply TEXT,
        state TEXT,
        style TEXT,
        success INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS style_stats (
        style TEXT PRIMARY KEY,
        success INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0
    )
    """)

    db.commit()
    return db, cur