# src/parser.py
# File parsing utilities for uploaded documents

import io
import streamlit as st
from docx import Document

def extract_text_from_upload(uploaded_file):
    """
    Extracts text content from uploaded Streamlit FileUploader objects
    based on their file type (TXT, DOCX, or PDF).
    """
    if uploaded_file is None:
        return None

    file_extension = uploaded_file.name.split('.')[-1].lower()
    file_bytes = uploaded_file.read()
    
    extracted_text = ""

    try:
        if file_extension == 'txt':
            extracted_text = file_bytes.decode('utf-8')
            st.info(f"Successfully parsed {uploaded_file.name} as plain text.")
            
        elif file_extension == 'docx':
            # Use io.BytesIO for compatibility with python-docx
            document = Document(io.BytesIO(file_bytes))
            extracted_text = "\n".join([para.text for para in document.paragraphs])
            st.info(f"Successfully parsed {uploaded_file.name} (DOCX).")
            
        elif file_extension == 'pdf':
            # WARNING: PDF parsing is highly complex and not implemented here.
            st.warning(f"⚠️ PDF file detected: {uploaded_file.name}. Please upload a TXT or DOCX for reliable results, or manually paste the content.")
            
    except Exception as e:
        st.error(f"Error processing {uploaded_file.name}: {e}")
        extracted_text = f"--- ERROR PARSING FILE: {e} ---"

    return extracted_text.strip()