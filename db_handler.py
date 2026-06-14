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


def insert_resume(
    resume_id: str, resume_link: str, db_name: str = "ats_database.db"
) -> bool:
    """Inserts a new resume record into the database.

    Returns True if successful, False otherwise.
    """
    insert_query = """
    INSERT INTO resumes (id, resume_link) 
    VALUES (?, ?);
    """
    try:
        with get_db_connection(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(insert_query, (resume_id, resume_link))
            conn.commit()
        print(f"Successfully inserted resume ID: {resume_id}")
        return True
    except sqlite3.IntegrityError:
        print(f"Error: A resume with ID '{resume_id}' already exists.")
        return False
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


# --- Example Usage ---
if __name__ == "__main__":
    DB_FILE = "ats_database.db"

    # 1. Initialize the database (Run this once at application startup)
    init_db(DB_FILE)

    # 2. Simulate data coming from your UI / backend routing
    mock_id_1 = "user_98765"
    mock_link_1 = "https://s3.amazonaws.com/ats-bucket/resumes/user_98765_cv.pdf"

    mock_id_2 = "user_12345"
    mock_link_2 = (
        "https://storage.googleapis.com/ats-resumes/cv_12345.docx"
    )

    # 3. Push data to the DB
    print("\n--- Inserting Records ---")
    insert_resume(mock_id_1, mock_link_1, DB_FILE)
    insert_resume(mock_id_2, mock_link_2, DB_FILE)

    # Test handling duplicate IDs
    print("\n--- Testing Duplicate Handling ---")
    insert_resume(mock_id_1, mock_link_1, DB_FILE)