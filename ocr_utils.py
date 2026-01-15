import cv2
import pytesseract
import numpy as np
import re
from pdf2image import convert_from_bytes
from PIL import Image


# -------------------------
# CLEAN OCR TEXT
# -------------------------
def clean_lines(text):
    lines = []
    for line in text.split("\n"):
        line = line.strip()
        if len(line) < 3:
            continue
        if sum(c.isalnum() for c in line) < 3:
            continue
        line = re.sub(r"\s+", " ", line)
        lines.append(line)
    return lines


# -------------------------
# OCR IMAGE (MULTI-PASS)
# -------------------------
def ocr_image(img):
    texts = []

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Pass 1: Raw
    texts.append(
        pytesseract.image_to_string(gray, config="--oem 3 --psm 6")
    )

    # Pass 2: Structure
    gray_blur = cv2.medianBlur(gray, 3)
    thresh = cv2.adaptiveThreshold(
        gray_blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        21, 7
    )
    texts.append(
        pytesseract.image_to_string(thresh, config="--oem 3 --psm 4")
    )

    # Pass 3: Contrast
    gray_contrast = cv2.equalizeHist(gray)
    texts.append(
        pytesseract.image_to_string(gray_contrast, config="--oem 3 --psm 6")
    )

    seen, final_lines = set(), []
    for t in texts:
        for line in clean_lines(t):
            key = line.lower()
            if key not in seen:
                final_lines.append(line)
                seen.add(key)

    return "\n".join(final_lines)


# -------------------------
# OCR PDF (ALL PAGES)
# -------------------------
def ocr_pdf_bytes(pdf_bytes):
    pages = convert_from_bytes(pdf_bytes, dpi=300)
    all_text = []

    for page in pages:
        img = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
        page_text = ocr_image(img)
        if page_text:
            all_text.append(page_text)

    return "\n".join(all_text)


# -------------------------
# OCR IMAGE BYTES (PNG/JPG)
# -------------------------
def ocr_image_bytes(image_bytes):
    img = Image.open(image_bytes).convert("RGB")
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    return ocr_image(img)
