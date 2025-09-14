from pydantic import BaseModel
from typing import Optional, List
import sqlite3

class Highlight(BaseModel):
    highlight_id: str
    user_id: str
    video_id: str
    clip_path: str
    title: str
    description: str
    hashtags: str
    status: str
    created_at: str

# In a real app, use an ORM like SQLAlchemy for better management
def get_db_connection():
    conn = sqlite3.connect('highlights.db')
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def create_table():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS highlights (
            highlight_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            video_id TEXT NOT NULL,
            clip_path TEXT NOT NULL,
            title TEXT,
            description TEXT,
            hashtags TEXT,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_highlight_to_db(highlight: Highlight):
    conn = get_db_connection()
    conn.execute(
        """
        INSERT OR REPLACE INTO highlights (
            highlight_id, user_id, video_id, clip_path, title, description, hashtags, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            highlight.highlight_id,
            highlight.user_id,
            highlight.video_id,
            highlight.clip_path,
            highlight.title,
            highlight.description,
            highlight.hashtags,
            highlight.status,
            highlight.created_at,
        ),
    )
    conn.commit()
    conn.close()

def get_ready_to_publish_highlights(user_id: str) -> List[Highlight]:
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM highlights WHERE user_id = ? AND status = 'READY_FOR_PUBLISHING'",
        (user_id,)
    )
    highlights = [Highlight(**dict(row)) for row in cursor.fetchall()]
    conn.close()
    return highlights