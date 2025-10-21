# main.py
import streamlit as st
from pdf_utils import upload_and_extract_pdf
from embeddings_utils import create_embeddings
from llm_utils import ask_question
import time
import itertools
import hashlib

# ---------------------------
# Page configuration
# ---------------------------
st.set_page_config(page_title="DocMind – PDF Q&A", page_icon="🤖", layout="wide")

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
    display: flex;
    flex-direction: column;
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
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-width: 900px;
    margin: 10px auto;
    max-height: 66vh;
    overflow-y: auto;
    padding: 12px;
    border-radius: 8px;
}
.user-msg {
    background-color: #a020f0;
    color: white;
    padding: 10px 14px;
    border-radius: 15px 15px 15px 0;
    max-width: 75%;
    align-self: flex-start;
    font-weight: bold;
}
.bot-msg {
    background-color: #4b0082;
    color: white;
    padding: 12px 16px;
    border-radius: 15px 15px 0 15px;
    max-width: 75%;
    align-self: flex-end;
    font-weight: bold;
    border: 1px solid #a020f0;
}
.top-input {
    width: 100%;
    max-width: 980px;
    margin: 10px auto;
    display: flex;
    gap: 10px;
    align-items: center;
}
.stTextInput>div>div>input {
    background-color: #d3d3d3;
    color: black;
    font-weight: bold;
    border-radius: 8px;
    padding: 12px;
    width: 100%;
    border: none;
}
.stButton>button {
    background-color: #a020f0;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 16px;
}
.stButton>button:hover {
    background-color: #8000c0;
}
.teddy {
    text-align: center;
    font-size: 18px;
    color: white;
}
.teddy img {
    width: 160px;
    animation: bounce 1.5s infinite;
}
@keyframes bounce {
    0%,100%{transform:translateY(0);}
    50%{transform:translateY(-8px);}
}
.footer {
    text-align: center;
    color: #a020f0;
    font-weight: bold;
    padding: 12px;
    margin-top: 12px;
    border-top: 2px solid #a020f0;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Sidebar: PDF Upload
# ---------------------------
st.sidebar.header("📄 Upload PDF")
with st.sidebar:
    pdf_text = upload_and_extract_pdf()
    st.markdown(
        """
        <div style="text-align:center; margin-top:24px; color:#a020f0; font-weight:bold;">
            📄 Ready to process your documents!<br>
            🧩 Drag & drop or upload a PDF to get started...
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------
# Main title
# ---------------------------
st.markdown('<div class="main-title">🤖 DocMind – PDF Q&A Assistant</div>', unsafe_allow_html=True)

# ---------------------------
# Initialize session
# ---------------------------
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "vectordb" not in st.session_state: st.session_state.vectordb = None
if "embeddings_ready" not in st.session_state: st.session_state.embeddings_ready = False
if "pdf_hash" not in st.session_state: st.session_state.pdf_hash = None

# ---------------------------
# Input form
# ---------------------------
with st.form(key="top_form", clear_on_submit=False):
    st.markdown('<div class="top-input">', unsafe_allow_html=True)
    user_input = st.text_input("Write your query here...", key="user_input", label_visibility="collapsed")
    submit = st.form_submit_button("Send")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Compute hash for uploaded PDF
# ---------------------------
def compute_text_hash(text: str):
    if not text: return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

current_pdf_hash = compute_text_hash(pdf_text)
is_new_upload = current_pdf_hash and current_pdf_hash != st.session_state.pdf_hash

# ---------------------------
# Process PDF and create embeddings
# ---------------------------
if is_new_upload:
    st.session_state.chat_history = []
    st.session_state.embeddings_ready = False
    st.session_state.pdf_hash = current_pdf_hash
    st.session_state.vectordb = None

    try:
        st.session_state.vectordb = create_embeddings(
            pdf_text,
            collection_name=f"policy_docs_{current_pdf_hash[:8]}",
            persist_dir=None  # ensures in-memory mode
        )
        st.session_state.embeddings_ready = True
    except Exception as e:
        st.error(f"❌ Failed to create embeddings for the new PDF: {e}")
        st.session_state.embeddings_ready = False

elif pdf_text and not st.session_state.embeddings_ready:
    with st.spinner("Preparing document..."):
        try:
            st.session_state.vectordb = create_embeddings(
                pdf_text,
                collection_name="policy_docs_temp",
                persist_dir=None
            )
            st.session_state.embeddings_ready = True
        except Exception as e:
            st.error(f"❌ Failed to prepare embeddings: {e}")
            st.session_state.embeddings_ready = False

# ---------------------------
# Handle user queries
# ---------------------------
if submit and user_input and user_input.strip():
    st.session_state.chat_history.insert(0, ("user", user_input.strip()))
    st.session_state.chat_history.insert(1, ("bot", "Generating answer..."))
    st.rerun()

placeholder_bot_index = next((i for i,(r,t) in enumerate(st.session_state.chat_history) if r=="bot" and t=="Generating answer..."), None)

if placeholder_bot_index is not None:
    loading_box = st.empty()
    for _ in range(4):
        loading_box.markdown("""
            <div class="teddy">
                <img src="https://media.tenor.com/_lYNcVvfWO8AAAAd/robot-teddy.gif">
                <p>🤖 Thinking deeply...</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(1.5)
    try:
        answer, docs = ask_question(user_input, st.session_state.vectordb)
    except Exception as e:
        answer, docs = f"Error while querying: {e}", []
    st.session_state.chat_history[placeholder_bot_index] = ("bot", answer)
    loading_box.empty()
    st.rerun()

# ---------------------------
# Render chat
# ---------------------------
if pdf_text:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for role, msg in st.session_state.chat_history:
        css_class = "user-msg" if role == "user" else "bot-msg"
        name = "You" if role == "user" else "Bot"
        st.markdown(f'<div class="{css_class}">{name} — {msg}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="teddy">
        <img src="https://media.tenor.com/_lYNcVvfWO8AAAAd/robot-teddy.gif">
        <p>🧸 Upload a PDF to get started!</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------
# Footer
# ---------------------------
st.markdown("""
<div class="footer">
    🤖 Powered by DocMind • Made with 💜 by Ayush Mishra ✨
</div>
""", unsafe_allow_html=True)
