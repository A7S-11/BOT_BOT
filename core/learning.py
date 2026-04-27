import logging

log = logging.getLogger(__name__)

def update_style_stats(cur, style: str, success: int):
    """
    تحديث إحصائيات الأسلوب لزيادة دقة اختيار الأسلوب الأنجح مستقبلاً.
    """
    try:
        # تحديث مباشر لأننا ضمنا وجود الأساليب في ملف db.py
        cur.execute(
            """
            UPDATE style_stats
            SET success = success + ?, total = total + 1
            WHERE style = ?
            """,
            (success, style)
        )
        # التأكد من الحفظ
        cur.connection.commit()
    except Exception as e:
        log.error(f"❌ Error updating style stats: {e}")


def mark_last_success(cur):
    """
    يُستخدم هذا الفانكشن عادةً عند استلام رقم هاتف أو إتمام بيعة.
    """
    try:
        # جلب آخر رد قام به البوت
        row = cur.execute(
            "SELECT id, style FROM learning_data ORDER BY id DESC LIMIT 1"
        ).fetchone()

        if not row:
            return False

        last_id, style = row

        # تعليم الرد كـ ناجح
        cur.execute(
            "UPDATE learning_data SET success = 1 WHERE id = ?",
            (last_id,)
        )

        # تحديث إحصائيات الأسلوب الذي استُخدم في هذا الرد
        update_style_stats(cur, style, 1)
        
        cur.connection.commit()
        return True
    except Exception as e:
        log.error(f"❌ Error marking success: {e}")
        return False


def get_best_replies(cur, limit: int = 5):
    """
    جلب أفضل الردود التي أدت لنتائج ناجحة سابقاً لتزويد الـ AI بها (Few-shot prompting).
    """
    try:
        rows = cur.execute(
            """
            SELECT bot_reply FROM learning_data
            WHERE success = 1
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

        # إذا ماكو ردود ناجحة بعد، نرجع قائمة فارغة حتى ما يضرب الـ AI
        return [r[0] for r in rows] if rows else []
    except Exception as e:
        log.error(f"❌ Error getting best replies: {e}")
        return []
