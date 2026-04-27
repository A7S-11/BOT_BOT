import sqlite3
import os

def get_db():
    # تحديد مسار قاعدة البيانات (دعم للمجلدات في Railway)
    db_path = os.getenv("DB_PATH", "data.db")
    
    db = sqlite3.connect(db_path, check_same_thread=False)
    
    # تحسين الأداء ومنع الـ Database Lock
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=NORMAL")
    
    cur = db.cursor()

    # إنشاء الجداول
    cur.execute("""
    CREATE TABLE IF NOT EXISTS targets (
        id TEXT PRIMARY KEY
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        user_id INTEGER PRIMARY KEY,
        score INTEGER DEFAULT 0,
        state TEXT DEFAULT 'cold'
    )
    """)

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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # تحديث الـ Schema
    fix_schema(cur)

    db.commit()
    return db, cur

def fix_schema(cur):
    # قائمة بالأعمدة التي نريد التأكد من وجودها (طريقة أنظف)
    columns_to_add = [
        ("learning_data", "success", "INTEGER DEFAULT 0"),
        ("learning_data", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ("clients", "score", "INTEGER DEFAULT 0"),
        ("clients", "state", "TEXT DEFAULT 'cold'")
    ]

    for table, column, definition in columns_to_add:
        try:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        except sqlite3.OperationalError:
            # العمود موجود مسبقاً، نتجاهل الخطأ
            pass
