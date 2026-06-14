import streamlit as st
from pathlib import Path
from main import process_resume_upload

# 1. Page Configuration
st.set_page_config(page_title="ATS Resume Ingestion", page_icon="📄", layout="centered")

st.title("📄 Candidate Resume Ingestion Portal")
st.write("Upload a candidate's resume or provide a web link to index it into the ATS pipeline.")

st.divider()

# 2. Input Fields
candidate_id = st.text_input("Enter Candidate ID (e.g., user_123):", placeholder="Unique identifier...")

# Choose upload method
upload_method = st.radio("Select Upload Method:", ["Local File Upload", "Web URL / Path"])

final_url = None

if upload_method == "Local File Upload":
    uploaded_file = st.file_uploader("Choose a file (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    if uploaded_file:
        # Streamlit temporarily keeps uploaded files in memory.
        # We save it to a temporary local location so our resume_uploader can read it like a normal file.
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        temp_file_path = temp_dir / uploaded_file.name
        
        # Write bytes locally
        temp_file_path.write_bytes(uploaded_file.read())
        final_url = str(temp_file_path.resolve())

else:
    final_url = st.text_input("Enter Resume URL or local path:", placeholder="https://example.com/resume.pdf")

st.divider()

# 3. Submit Action
if st.button("🚀 Process & Ingest Resume", use_container_width=True):
    if not candidate_id.strip():
        st.error("❌ Please provide a valid Candidate ID.")
    elif not final_url:
        st.error("❌ Please provide a resume file or link.")
    else:
        with st.spinner("Processing pipeline (Downloading file & indexing to SQLite)..."):
            # Call your existing main.py logic directly
            success = process_resume_upload(candidate_id.strip(), final_url)
            
            if success:
                st.success(f"✅ Success! Candidate '{candidate_id}' has been successfully indexed.")
                st.balloons()
            else:
                st.error("❌ Something went wrong in the pipeline. Check terminal logs.")