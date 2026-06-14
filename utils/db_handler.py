import os
import sqlite3
from pathlib import Path
from typing import Optional

# Make the default DB path absolute, relative to this specific utils folder
UTILS_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = UTILS_DIR / "ats_database.db"


def get_db_connection(db_name: str = str(DEFAULT_DB_PATH)) -> sqlite3.Connection:
    """Establishes and returns a connection to the SQLite database."""
    return sqlite3.connect(db_name)


def init_db(db_name: str = str(DEFAULT_DB_PATH)) -> None:
    """Creates the SQLite database and the resumes table if they don't exist."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS resumes (
        id TEXT PRIMARY KEY,
        resume_link TEXT NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        with get_db_connection(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
        print(f"Database '{db_name}' initialized successfully.")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")


def save_or_update_resume(
    resume_id: str, resume_link: str, db_name: str = str(DEFAULT_DB_PATH)
) -> bool:
    """Inserts a new resume or overwrites the link if the ID already exists.

    Returns True if successful, False otherwise.
    """
    upsert_query = """
    INSERT OR REPLACE INTO resumes (id, resume_link, uploaded_at) 
    VALUES (?, ?, CURRENT_TIMESTAMP);
    """
    try:
        with get_db_connection(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(upsert_query, (resume_id, resume_link))
            conn.commit()
        print(f"Successfully saved/updated resume ID: {resume_id}")
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


if __name__ == "__main__":
    # Internal testing still works flawlessly
    init_db(str(DEFAULT_DB_PATH))
    save_or_update_resume("user_98765", "https://s3.amazonaws.com/ats-bucket/resumes/first_version.pdf")