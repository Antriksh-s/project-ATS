from pathlib import Path
import sys

# 1. Setup paths relative to this main file
BASE_DIR = Path(__file__).resolve().parent
UTILS_DIR = BASE_DIR / "utils"
DB_FILE = UTILS_DIR / "ats_database.db"
STORAGE_DIR = BASE_DIR / "resume_storage" # Folder where resumes will live

# 2. Import the functions from the utils directory
from utils.db_handler import init_db, save_or_update_resume
from utils.resume_uploader import upload_resume


def process_resume_upload(candidate_id: str, incoming_url: str) -> bool:
    """Orchestrates the resume processing pipeline.
    
    1. Downloads/Copies the resume into a local folder.
    2. Saves the absolute local file path into the SQLite database.
    """
    print(f"\n[Processing] Starting pipeline for Candidate ID: {candidate_id}")
    
    try:
        # Step A: Download or copy the file to local storage directory
        local_file_path = upload_resume(
            id=candidate_id, 
            url=incoming_url, 
            base_dir=STORAGE_DIR
        )
        print(f"[Storage] Successfully saved file to: {local_file_path}")
        
        # Step B: Record the permanent file path into SQLite
        db_success = save_or_update_resume(
            resume_id=candidate_id, 
            resume_link=local_file_path, 
            db_name=str(DB_FILE)
        )
        
        if db_success:
            print(f"[Database] Successfully indexed path for ID: {candidate_id}")
            print("[Success] Pipeline execution finished cleanly.")
            return True
        else:
            print("[Failure] Pipeline stopped: Database update failed.")
            return False
            
    except Exception as e:
        print(f"[Error] Pipeline broken: {e}")
        return False


if __name__ == "__main__":
    # Ensure the database file and table are ready on startup
    init_db(str(DB_FILE))
    
    # --- Simulating a UI Input Call ---
    # Case 1: New UI upload (Mocking an internet PDF link)
    sample_id = "user_abc456"
    sample_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    process_resume_upload(sample_id, sample_url)
    
    # Case 2: Overwrite upload (Same ID, updated version)
    # The uploader will overwrite the file, and the DB will overwrite the path mapping.
    print("\n--- Simulating a Re-upload / Overwrite ---")
    process_resume_upload(sample_id, sample_url)