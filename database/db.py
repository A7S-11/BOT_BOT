import sqlite3
import os

def get_db():
    # تحديد مسار قاعدة البيانات - يدعم Railway عبر المتغير البيئي DB_PATH
    # إذا لم يتم تحديد المتغير، سيتم إنشاء الملف في المجلد الرئيسي باسم data.db
    db_path = os.getenv("DB_PATH", "data.db")
    
    db = sqlite3.connect(db_path, check_same_thread=False)
    
    # تفعيل وضع WAL لزيادة الأداء ومنع الـ Database Lock أثناء عمل الـ Publisher والـ Handler معاً
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=NORMAL")
    
    cur = db.cursor()

    # ───── جداول الأهداف والرسائل ─────
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

    # ───── جدول العملاء وحالاتهم ─────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        user_id INTEGER PRIMARY KEY,
        score INTEGER DEFAULT 0,
        state TEXT DEFAULT 'cold'
    )
    """)

    # ───── جدول بيانات التعلم والذكاء الاصطناعي ─────
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

    # ───── جدول الإحصائيات (لأفضل أسلوب) ─────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS style_stats (
        style TEXT PRIMARY KEY,
        success INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0
    )
    """)

    # ───── جدول الإعدادات العامة ─────
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # ملء جدول الإحصائيات بالقيم الافتراضية إذا كان فارغاً
    for s in ["aggressive", "friendly", "expert", "scarcity"]:
        cur.execute("INSERT OR IGNORE INTO style_stats (style) VALUES (?)", (s,))

    # تحديث الـ Schema في حال وجود نسخة قديمة من قاعدة البيانات
    fix_schema(cur)

    db.commit()
    return db, cur

def fix_schema(cur):
    """دالة للتأكد من وجود الأعمدة الجديدة في حال تحديث البوت"""
    # قائمة بالأعمدة (اسم الجدول، اسم العمود، نوعه)
    updates = [
        ("learning_data", "success", "INTEGER DEFAULT 0"),
        ("learning_data", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ("clients", "score", "INTEGER DEFAULT 0"),
        ("clients", "state", "TEXT DEFAULT 'cold'"),
        ("style_stats", "total", "INTEGER DEFAULT 0")
    ]

    for table, col, definition in updates:
        try:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {definition}")
        except sqlite3.OperationalError:
            # العمود موجود مسبقاً، لا نفعل شيئاً
            pass

# إذا أردت تجربة الملف بشكل منفصل
if __name__ == "__main__":
    db, cur = get_db()
    print("✅ Database connection successful and tables are ready.")
