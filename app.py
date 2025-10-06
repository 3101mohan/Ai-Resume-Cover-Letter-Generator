import streamlit as st
import json
from src.prompts import RESUME_PROMPT_TEMPLATE, COVER_LETTER_PROMPT_TEMPLATE
from src.utils import generate_text_with_gemini
from src.export import create_docx_from_text, create_pdf_from_text
from src.parser import extract_text_from_upload

st.set_page_config(page_title="AI Resume & Cover Letter Generator", layout="wide")

st.title("♊ AI Resume & Cover Letter Generator")
st.markdown("Generate **ATS-friendly resumes** and **tailored cover letters** using Google's Gemini API.")

# --- INITIAL DATA STRUCTURE ---
# Initialize session state for persistent storage of parsed text across reruns
if 'parsed_resume_text_state' not in st.session_state:
    st.session_state.parsed_resume_text_state = ""
if 'parsed_jd_text_state' not in st.session_state:
    st.session_state.parsed_jd_text_state = ""

# --- FILE UPLOAD SECTION ---
st.subheader("📁 Upload Documents (Optional)")
st.caption("Uploaded content (TXT/DOCX) will populate the fields below.")
col_up1, col2 = st.columns(2)

# --- UPLOAD WIDGETS ---
with col_up1:
    uploaded_resume = st.file_uploader(
        "Upload Current Resume (TXT/DOCX)", 
        type=['txt', 'docx'], 
        key="uploaded_resume_file" 
    )
    
with col2:
    uploaded_jd = st.file_uploader(
        "Upload Job Description (TXT/DOCX)", 
        type=['txt', 'docx'], 
        key="uploaded_jd_file"
    )

# 2. Process file content *outside* of the form
# This is the reliable data parsing logic, run on every rerun after a file is uploaded.
if st.session_state.uploaded_resume_file is not None:
    current_file_hash = hash(st.session_state.uploaded_resume_file.read())
    st.session_state.uploaded_resume_file.seek(0)
    
    if st.session_state.parsed_resume_text_state == "" or 'resume_hash' not in st.session_state or st.session_state.resume_hash != current_file_hash:
        parsed_text = extract_text_from_upload(st.session_state.uploaded_resume_file)
        st.session_state.parsed_resume_text_state = parsed_text
        st.session_state.resume_hash = current_file_hash
    st.session_state.uploaded_resume_file.seek(0) # IMPORTANT: Reset pointer after processing

if st.session_state.uploaded_jd_file is not None:
    current_file_hash = hash(st.session_state.uploaded_jd_file.read())
    st.session_state.uploaded_jd_file.seek(0) 
    
    if st.session_state.parsed_jd_text_state == "" or 'jd_hash' not in st.session_state or st.session_state.jd_hash != current_file_hash:
        parsed_text = extract_text_from_upload(st.session_state.uploaded_jd_file)
        st.session_state.parsed_jd_text_state = parsed_text
        st.session_state.jd_hash = current_file_hash
    st.session_state.uploaded_jd_file.seek(0) # IMPORTANT: Reset pointer after processing

st.divider()

# --- INPUT FORM SECTION ---
with st.form("input_form"):
    st.subheader("Candidate Information")
    st.caption("Ensure the **Professional Summary** is filled with your resume content, either manually or via upload.")
    
    st.text_input("Full Name", key="name")
    st.text_input("Contact Info (Email / Phone / LinkedIn)", key="contact")
    
    st.text_area("Professional Summary (Full resume text is preferred here)", 
                           placeholder="Paste your full resume text here...", 
                           value=st.session_state.parsed_resume_text_state, 
                           height=200, key="summary_input")
    
    st.text_area("Skills (comma-separated)", key="skills_input")
    st.text_area("Education", key="education_input")
    st.text_area("Experience (Job Title | Company | Duration | Achievements)", key="experience_input")
    
    st.subheader("Job Description")
    st.caption("Paste the Job Description you are applying for to maximize your ATS score!")
    st.text_area("Paste Job Description", 
                            value=st.session_state.parsed_jd_text_state, 
                            height=200, key="jd_input")
    
    choice = st.selectbox("Generate:", ["Resume", "Cover Letter", "Both"], key="choice_input")
    submitted = st.form_submit_button("Generate")


# --- ATS JSON SCHEMA FOR GEMINI ---
ATS_JSON_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "ats_score": {"type": "STRING"},
        "keywords": {"type": "ARRAY", "items": {"type": "STRING"}},
        "resume_text": {"type": "STRING"}
    },
    "required": ["ats_score", "keywords", "resume_text"]
}


# --- GENERATION LOGIC ---
if submitted:
    
    final_summary = st.session_state.summary_input
    final_skills = st.session_state.skills_input
    final_education = st.session_state.education_input
    final_experience = st.session_state.experience_input
    final_job_desc = st.session_state.jd_input
    
    # Initialize variables to prevent NameError if generation fails
    resume_text = ""
    cover_text = ""
    
    if not st.session_state.name or not final_summary or not final_job_desc:
        st.error("⚠️ CRITICAL: Full Name, Resume Content (Summary), and Job Description must be provided for ATS optimization.")
    else:
        try:
            resume_data = None

            # --- Resume Generation (JSON Structured) ---
            if st.session_state.choice_input in ["Resume", "Both"]:
                rp = RESUME_PROMPT_TEMPLATE.format(
                    name=st.session_state.name, contact=st.session_state.contact, 
                    summary=final_summary, skills=final_skills,
                    experience=final_experience, education=final_education,
                    job_description=final_job_desc
                )
                with st.spinner('Generating ATS-optimized Resume and scoring...'):
                    # Expecting a JSON response
                    json_output = generate_text_with_gemini(
                        rp, 
                        max_output_tokens=1024,
                        response_json_schema=ATS_JSON_SCHEMA 
                    )
                
                # Parse the JSON output
                try:
                    resume_data = json.loads(json_output)
                    resume_text = resume_data.get("resume_text", "Error: Resume text not found in JSON.")
                    ats_score = resume_data.get("ats_score", "N/A")
                    keywords = resume_data.get("keywords", [])
                except json.JSONDecodeError as e:
                    resume_text = f"⚠️ Error decoding JSON output from Gemini. Check raw output in Debugger. Error: {e}"
                    ats_score = "N/A"
                    keywords = []

                # TEMPORARY DEBUGGING AID: SHOW PROMPT
                with st.expander("📝 View Final Resume Prompt (for debugging empty response)"):
                    st.text(rp)
                    st.text("--- Raw Gemini Output ---")
                    st.json(json_output)


            # --- Cover Letter Generation (Original text output) ---
            if st.session_state.choice_input in ["Cover Letter", "Both"]:
                cp = COVER_LETTER_PROMPT_TEMPLATE.format(
                    name=st.session_state.name, contact=st.session_state.contact, 
                    summary=final_summary, skills=final_skills,
                    experience=final_experience, education=final_education, job_description=final_job_desc
                )
                with st.spinner('Tailoring Cover Letter to Job Description...'):
                    cover_text = generate_text_with_gemini(cp, max_output_tokens=400)

            # --- Display ATS Score and Keywords ---
            if resume_data and isinstance(resume_data, dict) and "resume_text" in resume_data:
                st.subheader("📄 Generated Resume & ATS Analysis")
                
                col_score, col_keywords = st.columns([1, 2])
                
                with col_score:
                    # Display the ATS Score
                    st.metric(label="Estimated ATS Match Score", value=ats_score)
                    
                with col_keywords:
                    # Display the Keywords
                    st.markdown("##### Keywords Incorporated")
                    st.markdown(f"**Targeted Keywords:** {', '.join(keywords)}")

                # Display Resume Preview
                st.text_area("Resume Preview", value=resume_text, height=400)
                
                # --- FINAL FIX: ISOLATE DOWNLOAD BUTTONS (Resume) ---
                st.markdown("---")
                st.subheader("Download Resume")
                col_res_dl1, col_res_dl2 = st.columns([1, 10]) 
                
                with col_res_dl1:
                    st.download_button("Download DOCX", create_docx_from_text(f"{st.session_state.name} - Resume", resume_text),
                                       file_name=f"{st.session_state.name}_Resume.docx")
                with col_res_dl2:
                    st.download_button("Download PDF", create_pdf_from_text(f"{st.session_state.name} - Resume", resume_text),
                                       file_name=f"{st.session_state.name}_Resume.pdf")
            elif resume_text.startswith("⚠️"):
                 st.error(resume_text) 

            # --- Display and Download Cover Letter (If successful) ---
            if cover_text and not cover_text.startswith("⚠️"):
                st.subheader("✉️ Generated Cover Letter")
                st.text_area("Cover Letter Preview", value=cover_text, height=250)
                
                # --- FINAL FIX: ISOLATE DOWNLOAD BUTTONS (Cover Letter) ---
                st.markdown("---")
                st.subheader("Download Cover Letter")
                col_cl_dl1, col_cl_dl2 = st.columns([1, 10]) 
                
                with col_cl_dl1:
                    st.download_button("Download DOCX", create_docx_from_text(f"{st.session_state.name} - Cover Letter", cover_text),
                                       file_name=f"{st.session_state.name}_CoverLetter.docx")
                with col_cl_dl2:
                    st.download_button("Download PDF", create_pdf_from_text(f"{st.session_state.name} - Cover Letter", cover_text),
                                       file_name=f"{st.session_state.name}_CoverLetter.pdf")
            elif cover_text.startswith("⚠️"):
                st.error(cover_text) 

            st.success("✅ Documents generation attempted.")

        except Exception as e:
            st.error(f"Critical Application Error: {e}")
