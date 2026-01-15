# main.py
import streamlit as st
import time
import hashlib

from pdf_utils import upload_and_extract_file
from embeddings_utils import create_embeddings
from llm_utils import ask_question
from question_suggestions import generate_smart_questions

# ---------------------------
# Page configuration
# ---------------------------
st.set_page_config(
    page_title="DocMind – Document Intelligence",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------
# GLOBAL CSS (ROYAL BLUE THEME)
# ---------------------------
st.markdown("""
<style>
:root {
    --primary: #1e90ff;
    --secondary: #0b3c6f;
    --accent: #4da3ff;
    --background: #050b17;
}

.stApp {
    background: radial-gradient(circle at top, #0b1a33, var(--background));
    color: white;
    min-height: 100vh;
}

/* Main title */
.main-title {
    color: var(--primary);
    font-size: 44px;
    font-weight: 800;
    text-align: center;
    padding: 16px;
    border-radius: 16px;
    background: linear-gradient(135deg, #07152c, #0b3c6f);
    box-shadow: 0 0 25px rgba(30,144,255,0.35);
    margin-bottom: 25px;
}

/* Suggested question container */
.suggestion-box {
    margin-top: 10px;
    padding: 18px;
    border-radius: 16px;
    background: linear-gradient(135deg, #07152c, #0b3c6f);
    box-shadow: 0 0 20px rgba(30,144,255,0.25);
}

/* Buttons (question chips) */
.stButton>button {
    background: linear-gradient(135deg, #1e90ff, #4da3ff);
    color: black;
    border-radius: 999px;
    padding: 10px 18px;
    font-weight: 700;
    border: none;
    margin: 6px 6px 6px 0;
    transition: all 0.25s ease;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 15px rgba(77,163,255,0.6);
}

/* Chat bubbles */
.user-msg {
    background: linear-gradient(135deg, var(--primary), var(--accent));
    color: black;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 4px;
    max-width: 75%;
    font-weight: 600;
    margin-bottom: 8px;
}

.bot-msg {
    background: linear-gradient(135deg, #0b3c6f, #07152c);
    color: white;
    padding: 14px 18px;
    border-radius: 18px 18px 4px 18px;
    border: 1px solid var(--primary);
    box-shadow: 0 0 10px rgba(30,144,255,0.25);
    max-width: 75%;
    margin-bottom: 8px;
}

/* Footer */
.footer {
    text-align: center;
    color: var(--accent);
    font-weight: 700;
    margin-top: 30px;
    padding: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.header("📄 Upload Document")
document_text = upload_and_extract_file()

st.sidebar.markdown("""
<div style="
    margin-top: 25px;
    padding: 16px;
    border-radius: 14px;
    background: linear-gradient(135deg, #07152c, #0b3c6f);
    box-shadow: 0 0 18px rgba(30,144,255,0.25);
">
    <h4 style="color:#4da3ff;">🧠 DocMind Intelligence</h4>
    <ul style="color:white; font-size:14px;">
        <li>📄 PDF & Image Support</li>
        <li>🔍 OCR for Scanned Docs</li>
        <li>🧠 Smart Question Suggestions</li>
        <li>⚡ Gemini-Powered Answers</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# MAIN TITLE
# ---------------------------
st.markdown(
    '<div class="main-title">🤖 DocMind – Document Intelligence Assistant</div>',
    unsafe_allow_html=True
)

# ---------------------------
# SESSION STATE INIT
# ---------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "vectordb" not in st.session_state:
    st.session_state.vectordb = None

if "embeddings_ready" not in st.session_state:
    st.session_state.embeddings_ready = False

if "doc_hash" not in st.session_state:
    st.session_state.doc_hash = None

if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = []

# ---------------------------
# UTIL
# ---------------------------
def compute_hash(text):
    if not text:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

current_hash = compute_hash(document_text)
is_new_upload = current_hash and current_hash != st.session_state.doc_hash

# ---------------------------
# PROCESS NEW DOCUMENT
# ---------------------------
if is_new_upload:
    st.session_state.chat_history = []
    st.session_state.embeddings_ready = False
    st.session_state.doc_hash = current_hash
    st.session_state.vectordb = None
    st.session_state.suggested_questions = []

    with st.spinner("📄 Processing document..."):
        st.session_state.vectordb = create_embeddings(
            document_text,
            collection_name=f"docmind_{current_hash[:8]}",
            persist_dir=None
        )
        st.session_state.embeddings_ready = True

        st.session_state.suggested_questions = generate_smart_questions(
            document_text,
            max_questions=6
        )

# ---------------------------
# SUGGESTED QUESTIONS (ROYAL)
# ---------------------------
if st.session_state.suggested_questions:
    st.markdown('<div class="suggestion-box">', unsafe_allow_html=True)
    st.markdown("### 💡 Suggested Questions")

    for q in st.session_state.suggested_questions:
        if st.button(q, key=f"suggest_{q}"):
            st.session_state.chat_history.insert(0, ("user", q))
            st.session_state.chat_history.insert(1, ("bot", "Generating answer..."))
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# USER INPUT
# ---------------------------
with st.form("question_form", clear_on_submit=True):
    user_question = st.text_input("Ask a question about the document")
    submitted = st.form_submit_button("Send")

if submitted and user_question:
    st.session_state.chat_history.insert(0, ("user", user_question))
    st.session_state.chat_history.insert(1, ("bot", "Generating answer..."))
    st.rerun()

# ---------------------------
# ANSWER GENERATION
# ---------------------------
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

# ---------------------------
# CHAT RENDER
# ---------------------------
if document_text:
    for role, msg in st.session_state.chat_history:
        css = "user-msg" if role == "user" else "bot-msg"
        st.markdown(f'<div class="{css}">{msg}</div>', unsafe_allow_html=True)
else:
    st.info("📄 Upload a document to get started")

# ---------------------------
# FOOTER
# ---------------------------
st.markdown(
    '<div class="footer">🤖 Powered by DocMind • Built by Ayush Mishra ✨</div>',
    unsafe_allow_html=True
)
