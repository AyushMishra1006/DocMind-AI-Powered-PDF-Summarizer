import streamlit as st
import hashlib

from pdf_utils import upload_and_extract_file
from embeddings_utils import create_embeddings
from llm_utils import ask_question
from question_suggestions import generate_smart_questions

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="DocMind – Document Intelligence",
    page_icon="🤖",
    layout="wide"
)

# -------------------------------------------------
# SESSION STATE INIT (VERY IMPORTANT)
# -------------------------------------------------
defaults = {
    "app_loaded": False,
    "chat_history": [],
    "vectordb": None,
    "doc_hash": None,
    "suggested_questions": [],
    "processing": None,              # GLOBAL STATUS
    "pending_question": None,         # CLICK LOCK
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -------------------------------------------------
# SPLASH SCREEN (ONLY ONCE)
# -------------------------------------------------
if not st.session_state.app_loaded:
    st.markdown("""
    <style>
    .app-loader {
        position: fixed;
        inset: 0;
        background: black;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        z-index: 9999;
        animation: fadeOut 1s ease-out forwards;
        animation-delay: 3s;
    }
    @keyframes fadeOut {
        to { opacity: 0; visibility: hidden; }
    }
    .loader-text {
        font-size: 26px;
        font-weight: 800;
        color: white;
        margin-top: 18px;
        animation: pulse 1.4s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    </style>
    <div class="app-loader">
        <div style="font-size:72px;">🤖</div>
        <div class="loader-text">Loading DocMind…</div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# GLOBAL CSS (INJECT ONCE)
# -------------------------------------------------
if "css_loaded" not in st.session_state:
    st.session_state.css_loaded = True
    st.markdown("""<style>/* your CSS unchanged */</style>""", unsafe_allow_html=True)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.header("📄 Upload Document")
document_text = upload_and_extract_file()

# STATUS PANEL
if st.session_state.processing:
    st.sidebar.info(f"⚙️ {st.session_state.processing}")
else:
    st.sidebar.success("✅ Ready")

# -------------------------------------------------
# TITLE
# -------------------------------------------------
st.markdown(
    '<div class="main-title">🤖 DocMind – Document Intelligence Assistant</div>',
    unsafe_allow_html=True
)

# -------------------------------------------------
# HASHING
# -------------------------------------------------
def compute_hash(text):
    if not text:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

current_hash = compute_hash(document_text)
is_new_upload = current_hash and current_hash != st.session_state.doc_hash

# -------------------------------------------------
# DOCUMENT PROCESSING
# -------------------------------------------------
if is_new_upload:
    st.session_state.processing = "Processing document"
    st.session_state.chat_history.clear()
    st.session_state.doc_hash = current_hash
    st.session_state.vectordb = None
    st.session_state.suggested_questions.clear()

    st.session_state.vectordb = create_embeddings(
        document_text,
        collection_name=f"docmind_{current_hash[:8]}",
        persist_dir=None
    )

    st.session_state.suggested_questions = generate_smart_questions(
        document_text,
        max_questions=4
    )

    st.session_state.processing = None
    st.rerun()

# -------------------------------------------------
# SUGGESTED QUESTIONS (FIXED DUPLICATION)
# -------------------------------------------------
if st.session_state.suggested_questions and not st.session_state.pending_question:
    st.markdown("### 💡 Suggested Questions")
    col1, col2 = st.columns(2)

    for i, q in enumerate(st.session_state.suggested_questions):
        with (col1 if i % 2 == 0 else col2):
            if st.button(q, key=f"suggest_{i}"):
                st.session_state.pending_question = q
                st.session_state.processing = "Answering question"
                st.rerun()

# -------------------------------------------------
# USER INPUT
# -------------------------------------------------
with st.form("question_form", clear_on_submit=True):
    col1, col2 = st.columns([6, 1])
    user_question = col1.text_input(
        "Ask a question about the document",
        label_visibility="collapsed"
    )
    submitted = col2.form_submit_button("Send")

if submitted and user_question:
    st.session_state.pending_question = user_question
    st.session_state.processing = "Answering question"
    st.rerun()

# -------------------------------------------------
# ANSWER GENERATION (SINGLE EXECUTION GUARANTEED)
# -------------------------------------------------
if st.session_state.pending_question:
    q = st.session_state.pending_question
    st.session_state.chat_history.insert(0, ("user", q))
    st.session_state.chat_history.insert(1, ("bot", "Generating answer..."))

    answer, _ = ask_question(q, st.session_state.vectordb)
    st.session_state.chat_history[1] = ("bot", answer)

    st.session_state.pending_question = None
    st.session_state.processing = None
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
# MARK LOADED
# -------------------------------------------------
st.session_state.app_loaded = True

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown(
    '<div class="footer">🤖 Powered by DocMind • Built by Ayush Mishra ✨</div>',
    unsafe_allow_html=True
)
