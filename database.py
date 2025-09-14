# database.py
import sqlite3
import os

def get_db_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect('highlights.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    """Create highlights table if it doesn't exist"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS highlights (
            highlight_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            video_id TEXT NOT NULL,
            start_time REAL NOT NULL,
            end_time REAL NOT NULL,
            video_path TEXT NOT NULL,
            title TEXT,
            description TEXT,
            status TEXT DEFAULT 'PROCESSING',
            platform TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_highlight(highlight_id: str, user_id: str, video_id: str, start_time: float, 
                  end_time: float, video_path: str, title: str, description: str, status: str = "READY"):
    """Save highlight to database"""
    conn = get_db_connection()
    conn.execute(
        '''INSERT INTO highlights 
           (highlight_id, user_id, video_id, start_time, end_time, video_path, title, description, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (highlight_id, user_id, video_id, start_time, end_time, video_path, title, description, status)
    )
    conn.commit()
    conn.close()

def get_ready_to_publish_highlights(user_id: str):
    """Get highlights ready for publishing"""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM highlights WHERE user_id = ? AND status = 'READY'",
        (user_id,)
    )
    highlights = cursor.fetchall()
    conn.close()
    return highlights