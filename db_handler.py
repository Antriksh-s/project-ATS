import os
import sqlite3
from typing import Optional


def get_db_connection(db_name: str = "ats_database.db") -> sqlite3.Connection:
    """Establishes and returns a connection to the SQLite database."""
    return sqlite3.connect(db_name)


def init_db(db_name: str = "ats_database.db") -> None:
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
    resume_id: str, resume_link: str, db_name: str = "ats_database.db"
) -> bool:
    """Inserts a new resume or overwrites the link if the ID already exists.

    Returns True if successful, False otherwise.
    """
    # Changed INSERT INTO to INSERT OR REPLACE INTO
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


# --- Example Usage ---
if __name__ == "__main__":
    DB_FILE = "ats_database.db"

    # 1. Initialize the database
    init_db(DB_FILE)

    # 2. Mock Data
    mock_id = "user_98765"
    initial_link = "https://s3.amazonaws.com/ats-bucket/resumes/first_version.pdf"
    updated_link = "https://s3.amazonaws.com/ats-bucket/resumes/updated_version.pdf"

    # 3. First upload (Insert)
    print("\n--- Testing Initial Upload ---")
    save_or_update_resume(mock_id, initial_link, DB_FILE)

    # 4. Second upload with same ID but different link (Overwrite)
    print("\n--- Testing Re-upload (Overwrite) ---")
    save_or_update_resume(mock_id, updated_link, DB_FILE)