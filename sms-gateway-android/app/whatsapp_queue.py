import sqlite3
import os
from typing import Any, Dict, List, Optional

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "whatsapp_queue.db"
)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS whatsapp_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            to_number TEXT NOT NULL,
            message TEXT NOT NULL,
            tenant_id TEXT DEFAULT 'default',
            delivery_job_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def queue_messages(messages: List[Dict[str, Any]]) -> int:
    init_db()
    conn = get_connection()
    count = 0
    for msg in messages:
        conn.execute(
            "INSERT INTO whatsapp_queue (to_number, message, tenant_id, delivery_job_id) VALUES (?, ?, ?, ?)",
            (
                msg["to"],
                msg["message"],
                msg.get("tenant_id", "default"),
                msg.get("delivery_job_id"),
            ),
        )
        count += 1
    conn.commit()
    conn.close()
    return count


def get_next_message() -> Optional[Dict[str, Any]]:
    init_db()
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM whatsapp_queue ORDER BY id ASC LIMIT 1"
    ).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def delete_message(message_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM whatsapp_queue WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()


def count_queued() -> int:
    init_db()
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM whatsapp_queue").fetchone()[0]
    conn.close()
    return count


def clear_queue() -> None:
    conn = get_connection()
    conn.execute("DELETE FROM whatsapp_queue")
    conn.commit()
    conn.close()


def get_all_messages() -> List[Dict[str, Any]]:
    init_db()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM whatsapp_queue ORDER BY id ASC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
