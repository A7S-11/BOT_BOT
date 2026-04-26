# core/learning.py

def update_style_stats(cur, style: str, success: int):
    """
    تحديث إحصائيات الأسلوب:
    success = 1 إذا الصفقة نجحت، 0 إذا لا
    """
    # حاول تحدّث، وإذا ما موجود أضِف
    row = cur.execute(
        "SELECT style FROM style_stats WHERE style = ?",
        (style,)
    ).fetchone()

    if row:
        cur.execute(
            """
            UPDATE style_stats
            SET success = success + ?, total = total + 1
            WHERE style = ?
            """,
            (success, style)
        )
    else:
        cur.execute(
            """
            INSERT INTO style_stats (style, success, total)
            VALUES (?, ?, 1)
            """,
            (style, success)
        )


def mark_last_success(cur):
    """
    تعليم آخر رد كـ صفقة ناجحة + تحديث إحصائيات الأسلوب
    """
    row = cur.execute(
        "SELECT id, style FROM learning_data ORDER BY id DESC LIMIT 1"
    ).fetchone()

    if not row:
        return False

    last_id, style = row

    cur.execute(
        "UPDATE learning_data SET success = 1 WHERE id = ?",
        (last_id,)
    )

    # حدّث أداء الأسلوب
    update_style_stats(cur, style, 1)

    return True


def get_best_replies(cur, limit: int = 10):
    """
    جلب أفضل الردود الناجحة لاستخدامها داخل AI
    """
    rows = cur.execute(
        """
        SELECT bot_reply FROM learning_data
        WHERE success = 1
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()

    return [r[0] for r in rows]