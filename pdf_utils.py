import pdfplumber
import streamlit as st
from ocr_utils import ocr_pdf_bytes, ocr_image_bytes


# -------------------------
# TEXT QUALITY CHECK
# -------------------------
def is_text_good(text):
    if not text:
        return False
    if len(text) < 50:
        return False
    if len(text.split()) < 10:
        return False
    alnum_ratio = sum(c.isalnum() for c in text) / max(len(text), 1)
    return alnum_ratio > 0.3


# -------------------------
# MAIN INGESTION FUNCTION
# -------------------------
def upload_and_extract_file():
    uploaded_file = st.sidebar.file_uploader(
        "",
        type=["pdf", "png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )

    if uploaded_file is None:
        return None

    file_type = uploaded_file.type

    # ---------- IMAGE ----------
    if file_type.startswith("image"):
        st.sidebar.info("🖼 Image detected. Running OCR...")
        return ocr_image_bytes(uploaded_file)

    # ---------- PDF ----------
    pdf_bytes = uploaded_file.read()
    collected_text = []

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(x_tolerance=1, y_tolerance=1)
            if is_text_good(page_text):
                collected_text.append(page_text)

    native_text = "\n".join(collected_text)

    if not is_text_good(native_text):
        st.sidebar.info("🔍 Scanned or mixed PDF detected. Running OCR...")
        return ocr_pdf_bytes(pdf_bytes)

    return native_text.strip()

#
