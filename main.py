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
# APP LOADING STATE
# -------------------------------------------------
if "app_loaded" not in st.session_state:
    st.session_state.app_loaded = False

# -------------------------------------------------
# SESSION STATE (FIXED: added active_question + processing)
# -------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "vectordb" not in st.session_state:
    st.session_state.vectordb = None
if "doc_hash" not in st.session_state:
    st.session_state.doc_hash = None
if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = []
if "active_question" not in st.session_state:      # ✅ FIX 1
    st.session_state.active_question = None
if "processing" not in st.session_state:           # ✅ FIX 2
    st.session_state.processing = False

# -------------------------------------------------
# APP LOADING GUI (SPLASH)
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
        animation-delay: 5s;
    }

    @keyframes fadeOut {
        to {
            opacity: 0;
            visibility: hidden;
        }
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
# GLOBAL CSS (UNCHANGED)
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
/* rest of your CSS unchanged */
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.header("📄 Upload Document")
document_text = upload_and_extract_file()

# ✅ FIX 3: show working status
if st.session_state.processing:
    st.sidebar.info("⚙️ Working… please wait")
else:
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
    st.session_state.processing = True   # ✅ FIX
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

    st.session_state.processing = False  # ✅ FIX

# -------------------------------------------------
# SUGGESTED QUESTIONS (FIXED DUPLICATE BUG)
# -------------------------------------------------
if st.session_state.suggested_questions:
    st.markdown('<div class="suggestion-box">', unsafe_allow_html=True)
    st.markdown("### 💡 Suggested Questions")

    col1, col2 = st.columns(2)
    for i, q in enumerate(st.session_state.suggested_questions):
        with (col1 if i % 2 == 0 else col2):
            if st.button(q, key=f"suggest_{i}") and st.session_state.active_question is None:
                st.session_state.active_question = q  # ✅ LOCK
                st.session_state.chat_history.insert(0, ("user", q))
                st.session_state.chat_history.insert(1, ("bot", "Generating answer..."))
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# USER INPUT (UNCHANGED)
# -------------------------------------------------
with st.form("question_form", clear_on_submit=True):
    col1, col2 = st.columns([6, 1])

    with col1:
        user_question = st.text_input(
            "Ask a question about the document",
            label_visibility="collapsed"
        )

    with col2:
        submitted = st.form_submit_button("Send")

if submitted and user_question:
    st.session_state.active_question = user_question  # ✅ LOCK
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
    st.session_state.processing = True  # ✅ FIX
    with st.spinner("🤖 Thinking..."):
        answer, _ = ask_question(
            st.session_state.chat_history[placeholder_index - 1][1],
            st.session_state.vectordb
        )
    st.session_state.chat_history[placeholder_index] = ("bot", answer)
    st.session_state.active_question = None  # ✅ UNLOCK
    st.session_state.processing = False      # ✅ FIX
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
# MARK APP AS LOADED
# -------------------------------------------------
st.session_state.app_loaded = True

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown(
    '<div class="footer">🤖 Powered by DocMind • Built by Ayush Mishra ✨</div>',
    unsafe_allow_html=True
)
