import sqlite3
from datetime import datetime, timezone
from contextlib import contextmanager

DB_NAME = "messages.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def insert_message(email: str, content: str):
    conn = get_connection()
    cursor = conn.cursor()

    timestamp = datetime.now(timezone.utc).isoformat()

    cursor.execute(
        "INSERT INTO messages (email, content, timestamp) VALUES (?, ?, ?)",
        (email, content, timestamp)
    )

    conn.commit()
    conn.close()


def get_all_messages():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT email, content, timestamp FROM messages")
    rows = cursor.fetchall()

    conn.close()
    return rows