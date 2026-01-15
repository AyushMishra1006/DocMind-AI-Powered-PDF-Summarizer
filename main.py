# main.py
import streamlit as st
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
# GLOBAL CSS (PURPLE THEME)
# ---------------------------
st.markdown("""
<style>
:root {
    --primary: #a020f0;
    --secondary: #4b0082;
    --accent: #d28cff;
    --background: #0b0014;
}

.stApp {
    background: radial-gradient(circle at top, #1a0028, var(--background));
    color: white;
    min-height: 100vh;
}

/* Main title */
.main-title {
    color: var(--accent);
    font-size: 44px;
    font-weight: 800;
    text-align: center;
    padding: 16px;
    border-radius: 16px;
    background: linear-gradient(135deg, #1a0028, #4b0082);
    box-shadow: 0 0 25px rgba(160,32,240,0.4);
    margin-bottom: 25px;
}

/* Suggested questions container */
.suggestion-box {
    margin-top: 10px;
    padding: 18px;
    border-radius: 16px;
    background: linear-gradient(135deg, #1a0028, #4b0082);
    box-shadow: 0 0 20px rgba(160,32,240,0.35);
}

/* Suggestion buttons */
.stButton>button {
    width: 100%;
    background: linear-gradient(135deg, #a020f0, #d28cff);
    color: black;
    border-radius: 999px;
    padding: 12px 18px;
    font-weight: 700;
    border: none;
    transition: all 0.25s ease;
}

.stButton>button:hover {
    transform: scale(1.04);
    box-shadow: 0 0 14px rgba(210,140,255,0.7);
}

/* Chat bubbles */
.user-msg {
    background: linear-gradient(135deg, #a020f0, #d28cff);
    color: black;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 4px;
    max-width: 75%;
    font-weight: 600;
    margin-bottom: 8px;
}

.bot-msg {
    background: linear-gradient(135deg, #4b0082, #1a0028);
    color: white;
    padding: 14px 18px;
    border-radius: 18px 18px 4px 18px;
    border: 1px solid #a020f0;
    box-shadow: 0 0 10px rgba(160,32,240,0.35);
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
    background: linear-gradient(135deg, #1a0028, #4b0082);
    box-shadow: 0 0 18px rgba(160,32,240,0.35);
">
    <h4 style="color:#d28cff;">🧠 DocMind Intelligence</h4>
    <ul style="color:white; font-size:14px;">
        <li>📄 PDF & Image Support</li>
        <li>🔍 OCR for Scanned Docs</li>
        <li>🧠 Smart Questions</li>
        <li>⚡ Gemini-Powered Answers</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# TITLE
# ---------------------------
st.markdown(
    '<div class="main-title">🤖 DocMind – Document Intelligence Assistant</div>',
    unsafe_allow_html=True
)

# ---------------------------
# SESSION STATE
# ---------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "vectordb" not in st.session_state:
    st.session_state.vectordb = None

if "doc_hash" not in st.session_state:
    st.session_state.doc_hash = None

if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = []

# ---------------------------
# HASH UTILITY
# ---------------------------
def compute_hash(text):
    if not text:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

current_hash = compute_hash(document_text)
is_new_upload = current_hash and current_hash != st.session_state.doc_hash

# ---------------------------
# PROCESS DOCUMENT
# ---------------------------
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

        # 🔥 ONLY 4 SMART QUESTIONS
        st.session_state.suggested_questions = generate_smart_questions(
            document_text,
            max_questions=4
        )

# ---------------------------
# SUGGESTED QUESTIONS (2x2 GRID)
# ---------------------------
if st.session_state.suggested_questions:
    st.markdown('<div class="suggestion-box">', unsafe_allow_html=True)
    st.markdown("### 💡 Suggested Questions")

    q = st.session_state.suggested_questions
    col1, col2 = st.columns(2)

    for i, question in enumerate(q):
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            if st.button(question, key=f"suggest_{i}"):
                st.session_state.chat_history.insert(0, ("user", question))
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
