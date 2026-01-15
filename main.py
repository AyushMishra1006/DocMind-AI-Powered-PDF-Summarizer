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
    page_title="DocMind – Document Q&A",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------
# CSS Styling
# ---------------------------
st.markdown("""
<style>
.stApp {
    background-color: black;
    color: white;
    background-image: url("https://www.transparenttextures.com/patterns/stardust.png");
    background-size: cover;
    min-height: 100vh;
}
.main-title {
    color: #a020f0;
    font-size: 42px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 10px;
    padding: 12px;
    border: 2px solid #a020f0;
    border-radius: 12px;
    background: linear-gradient(90deg, black, #2b004d);
}
.chat-container {
    max-width: 900px;
    margin: auto;
    max-height: 65vh;
    overflow-y: auto;
    padding: 12px;
}
.user-msg {
    background-color: #a020f0;
    padding: 10px;
    border-radius: 15px 15px 15px 0;
    margin-bottom: 8px;
}
.bot-msg {
    background-color: #4b0082;
    padding: 12px;
    border-radius: 15px 15px 0 15px;
    margin-bottom: 8px;
    border: 1px solid #a020f0;
}
.footer {
    text-align: center;
    color: #a020f0;
    font-weight: bold;
    margin-top: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Sidebar: Upload
# ---------------------------
st.sidebar.header("📄 Upload Document")
document_text = upload_and_extract_file()

# ---------------------------
# Title
# ---------------------------
st.markdown('<div class="main-title">🤖 DocMind – Document Q&A Assistant</div>', unsafe_allow_html=True)

# ---------------------------
# Session State Init
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
# Utility
# ---------------------------
def compute_hash(text):
    if not text:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

current_hash = compute_hash(document_text)
is_new_upload = current_hash and current_hash != st.session_state.doc_hash

# ---------------------------
# Process New Upload
# ---------------------------
if is_new_upload:
    st.session_state.chat_history = []
    st.session_state.embeddings_ready = False
    st.session_state.doc_hash = current_hash
    st.session_state.vectordb = None
    st.session_state.suggested_questions = []

    with st.spinner("📄 Processing document..."):
        try:
            st.session_state.vectordb = create_embeddings(
                document_text,
                collection_name=f"docmind_{current_hash[:8]}",
                persist_dir=None
            )
            st.session_state.embeddings_ready = True

            # 🔥 Generate Smart Question Suggestions (ONCE)
            st.session_state.suggested_questions = generate_smart_questions(
                document_text,
                max_questions=6
            )

        except Exception as e:
            st.error(f"❌ Failed to process document: {e}")

# ---------------------------
# Suggested Questions UI
# ---------------------------
if st.session_state.suggested_questions:
    st.markdown("### 💡 Suggested Questions")
    cols = st.columns(len(st.session_state.suggested_questions))
    for col, q in zip(cols, st.session_state.suggested_questions):
        if col.button(q):
            st.session_state.chat_history.insert(0, ("user", q))
            st.session_state.chat_history.insert(1, ("bot", "Generating answer..."))
            st.rerun()

# ---------------------------
# User Input
# ---------------------------
with st.form("question_form", clear_on_submit=True):
    user_question = st.text_input("Ask a question about the document")
    submitted = st.form_submit_button("Send")

if submitted and user_question:
    st.session_state.chat_history.insert(0, ("user", user_question))
    st.session_state.chat_history.insert(1, ("bot", "Generating answer..."))
    st.rerun()

# ---------------------------
# Handle Answer Generation
# ---------------------------
placeholder_index = next(
    (i for i, (r, t) in enumerate(st.session_state.chat_history)
     if r == "bot" and t == "Generating answer..."),
    None
)

if placeholder_index is not None:
    with st.spinner("🤖 Thinking..."):
        try:
            answer, _ = ask_question(
                st.session_state.chat_history[placeholder_index - 1][1],
                st.session_state.vectordb
            )
        except Exception as e:
            answer = f"❌ Error: {e}"

    st.session_state.chat_history[placeholder_index] = ("bot", answer)
    st.rerun()

# ---------------------------
# Render Chat
# ---------------------------
if document_text:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for role, msg in st.session_state.chat_history:
        css = "user-msg" if role == "user" else "bot-msg"
        st.markdown(f'<div class="{css}">{msg}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("📄 Upload a document to get started")

# ---------------------------
# Footer
# ---------------------------
st.markdown(
    '<div class="footer">🤖 Powered by DocMind • Built by Ayush Mishra ✨</div>',
    unsafe_allow_html=True
)
