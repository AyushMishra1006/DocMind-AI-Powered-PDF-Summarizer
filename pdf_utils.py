import pdfplumber
import streamlit as st

def upload_and_extract_pdf():
    """Handles PDF upload and extracts clean text using pdfplumber."""
    uploaded_file = st.sidebar.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded_file is not None:
        text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                # Extract text with better layout handling
                page_text = page.extract_text(x_tolerance=1, y_tolerance=1)
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    return None
