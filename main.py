# main.py
import streamlit as st
import hashlib

from pdf_utils import upload_and_extract_file
from embeddings_utils import create_embeddings
from llm_utils import ask_question
from question_suggestions import generate_smart_questions

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="DocMind – Document Intelligence",
    page_icon="🤖",
    layout="wide"
)

# -------------------------------------------------
# GLOBAL CSS (LOCKED DARK THEME + STARS)
# -------------------------------------------------
st.markdown("""
<style>
:root {
    --accent: #a020f0;
    --accent-soft: rgba(160,32,240,0.35);
    --bg-main: #000000;
    --bg-soft: #0f0f0f;
    --bg-widget: #121212;
    --border-soft: rgba(255,255,255,0.15);
    --text-main: #ffffff;
    --text-muted: #cccccc;
}

/* App background */
.stApp {
    background-color: black !important;
    background-image:
        radial-gradient(circle at top, rgba(255,255,255,0.08), transparent 40%),
        url("https://www.transparenttextures.com/patterns/stardust.png");
    background-size: cover;
    color: var(--text-main) !important;
}

/* Remove Streamlit top bar */
header, .stToolbar {
    background: black !important;
    box-shadow: none !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0b0b0b !important;
    border-right: 1px solid var(--border-soft);
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: var(--bg-soft) !important;
    border-radius: 12px;
    border: 1px solid var(--border-soft);
}
[data-testid="stFileUploader"] * {
    color: var(--text-main) !important;
}

/* Text inputs */
input, textarea {
    background-color: var(--bg-widget) !important;
    color: var(--text-main) !important;
    border-radius: 10px !important;
    border: 1px solid var(--border-soft) !important;
}
input::placeholder {
    color: var(--text-muted) !important;
}

/* Buttons */
button {
    background-color: var(--bg-widget) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 999px !important;
    padding: 10px 18px !important;
    font-weight: 600;
}
button:hover {
    background-color: var(--accent) !important;
    color: black !important;
}

/* Labels & text */
label, .stMarkdown {
    color: var(--text-main) !important;
}

/* Title */
.main-title {
    background: #0f0f0f !important;
    border: 1px solid var(--accent);
    box-shadow: 0 0 18px var(--accent-soft);
    border-radius: 14px;
    padding: 14px;
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 24px;
}

/* Sidebar console */
.sidebar-console {
    margin-top: 20px;
    padding: 16px;
    border-radius: 14px;
    background: #0f0f0f;
    border: 1px solid var(--border-soft);
    font-family: monospace;
    font-size: 14px;
    line-height: 1.6;
}

/* Suggestions box */
.suggestion-box {
    margin-top: 14px;
    padding: 16px;
    border-radius: 14px;
    background: #0f0f0f;
    border: 1px solid var(--border-soft);
}

/* Chat bubbles */
.user-msg {
    background: #181818;
    border-left: 4px solid var(--accent);
    padding: 12px 16px;
    border-radius: 14px;
    max-width: 75%;
    margin-bottom: 8px;
}
.bot-msg {
    background: #101010;
    border-right: 4px solid var(--accent);
    padding: 14px 18px;
    border-radius: 14px;
    max-width: 75%;
    margin-bottom: 8px;
}

/* Footer */
.footer {
    text-align: center;
    color: #bbbbbb;
    font-weight: 600;
    margin-top: 30px;
    padding: 15px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.header("📄 Upload Document")
document_text = upload_and_extract_file()

st.sidebar.markdown("""
<div class="sidebar-console">
▸ STATUS   : READY<br>
▸ MODE     : DOCUMENT INTELLIGENCE<br>
▸ INPUT    : PDF / IMAGE<br>
▸ ENGINE   : OCR + GEMINI<br>
▸ STATE    : AWAITING QUERY
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# TITLE
# -------------------------------------------------
st.markdown(
    '<div class="main-title">🤖 DocMind – Document Intelligence Assistant</div>',
    unsafe_allow_html=True
)

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "vectordb" not in st.session_state:
    st.session_state.vectordb = None
if "doc_hash" not in st.session_state:
    st.session_state.doc_hash = None
if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = []

# -------------------------------------------------
# HASH
# -------------------------------------------------
def compute_hash(text):
    if not text:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

current_hash = compute_hash(document_text)
is_new_upload = current_hash and current_hash != st.session_state.doc_hash

# -------------------------------------------------
# PROCESS DOCUMENT
# -------------------------------------------------
if is_new_upload:
    st.session_state.chat_history = []
    st.session_state.doc_hash = current_hash
    st.session_state.vectordb = None
    st.session_state.suggested_questions = []

    with st.spinner("📄 Processing document..."):
        st.session_state.vectordb = create_embeddings(
            document_text,
            collection_name=f"docmind_{current_hash[:8]}",
            persist_dir=None
        )
        st.session_state.suggested_questions = generate_smart_questions(
            document_text,
            max_questions=4
        )

# -------------------------------------------------
# SUGGESTED QUESTIONS (2x2)
# -------------------------------------------------
if st.session_state.suggested_questions:
    st.markdown('<div class="suggestion-box">', unsafe_allow_html=True)
    st.markdown("### 💡 Suggested Questions")

    col1, col2 = st.columns(2)
    for i, q in enumerate(st.session_state.suggested_questions):
        with (col1 if i % 2 == 0 else col2):
            if st.button(q, key=f"suggest_{i}"):
                st.session_state.chat_history.insert(0, ("user", q))
                st.session_state.chat_history.insert(1, ("bot", "Generating answer..."))
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# USER INPUT
# -------------------------------------------------
with st.form("question_form", clear_on_submit=True):
    user_question = st.text_input("Ask a question about the document")
    submitted = st.form_submit_button("Send")

if submitted and user_question:
    st.session_state.chat_history.insert(0, ("user", user_question))
    st.session_state.chat_history.insert(1, ("bot", "Generating answer..."))
    st.rerun()

# -------------------------------------------------
# ANSWER GENERATION
# -------------------------------------------------
placeholder_index = next(
    (i for i, (r, t) in enumerate(st.session_state.chat_history)
     if r == "bot" and t == "Generating answer..."),
    None
)

if placeholder_index is not None:
    with st.spinner("🤖 Thinking..."):
        answer, _ = ask_question(
            st.session_state.chat_history[placeholder_index - 1][1],
            st.session_state.vectordb
        )
    st.session_state.chat_history[placeholder_index] = ("bot", answer)
    st.rerun()

# -------------------------------------------------
# CHAT RENDER
# -------------------------------------------------
if document_text:
    for role, msg in st.session_state.chat_history:
        css = "user-msg" if role == "user" else "bot-msg"
        st.markdown(f'<div class="{css}">{msg}</div>', unsafe_allow_html=True)
else:
    st.info("📄 Upload a document to get started")

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown(
    '<div class="footer">🤖 Powered by DocMind • Built by Ayush Mishra ✨</div>',
    unsafe_allow_html=True
)
