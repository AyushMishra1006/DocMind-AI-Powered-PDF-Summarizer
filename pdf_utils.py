# pdf_utils.py
import fitz  # PyMuPDF
import streamlit as st
def upload_and_extract_pdf():
    uploaded_file = st.sidebar.file_uploader("📄 Upload your PDF", type=["pdf"])
    if uploaded_file is not None:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text("text")
        # Clean & normalize the text
        text = text.replace('\n', ' ').replace('\r', ' ')
        return text
    return None
