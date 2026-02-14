import sqlite3
from datetime import datetime
from database import get_connection

def send_notification(user_id, role, message):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO notifications (user_id, role, message, created_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, role, message, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()


def get_notifications(user_id, role):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, message, created_at
        FROM notifications
        WHERE user_id=? AND role=? AND is_read=0
        ORDER BY id DESC
    """, (user_id, role))
    data = cur.fetchall()
    conn.close()
    return data


def mark_as_read(notification_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE notifications SET is_read=1 WHERE id=?
    """, (notification_id,))
    conn.commit()
    conn.close()
