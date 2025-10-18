# main.py
import streamlit as st
from pdf_utils import upload_and_extract_pdf
from embeddings_utils import create_embeddings, clear_all_collections
from llm_utils import ask_question
import time
import itertools
import hashlib

# ---------------------------
# Page configuration
# ---------------------------
st.set_page_config(
    page_title="DocMind – PDF Q&A",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------
# CSS Styling (same as before)
# ---------------------------
st.markdown("""
<style>
.stApp { background-color: black; color: white; }
.main-title { color: #a020f0; font-size: 42px; font-weight: bold; text-align:center; }
.chat-container { display:flex; flex-direction:column; gap:10px; max-width:900px; margin:10px auto; max-height:66vh; overflow-y:auto; padding:12px; border-radius:8px; }
.user-msg { background-color:#a020f0; color:white; padding:10px 14px; border-radius:15px 15px 15px 0; max-width:75%; align-self:flex-start; font-weight:bold; }
.bot-msg { background-color:#4b0082; color:white; padding:12px 16px; border-radius:15px 15px 0 15px; max-width:75%; align-self:flex-end; font-weight:bold; border:1px solid #a020f0; }
.top-input { width:100%; max-width:980px; margin:10px auto; display:flex; gap:10px; align-items:center; }
.stTextInput>div>div>input { background-color:#d3d3d3; color:black; font-weight:bold; border-radius:8px; padding:12px; width:100%; border:none; }
.stButton>button { background-color:#a020f0; color:white; font-weight:bold; border-radius:8px; padding:10px 20px; font-size:16px; }
.stButton>button:hover { background-color:#8000c0; }
.teddy { text-align:center; font-size:18px; color:white; margin-top:8px; margin-bottom:8px; }
.footer { text-align:center; color:#a020f0; font-weight:bold; padding:12px; margin-top:12px; border-top:2px solid #a020f0; }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Initialize session state
# ---------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "vectordb" not in st.session_state:
    st.session_state.vectordb = None
if "collection_name" not in st.session_state:
    st.session_state.collection_name = None
if "embeddings_ready" not in st.session_state:
    st.session_state.embeddings_ready = False
if "pdf_hash" not in st.session_state:
    st.session_state.pdf_hash = None
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = None

# ---------------------------
# Sidebar: PDF Upload
# ---------------------------
st.sidebar.header("📄 Upload PDF")
pdf_text = upload_and_extract_pdf()
if pdf_text:
    st.session_state.pdf_text = pdf_text

# ---------------------------
# Main title
# ---------------------------
st.markdown('<div class="main-title">🤖 DocMind – PDF Q&A Assistant</div>', unsafe_allow_html=True)

# ---------------------------
# Helper: compute hash
# ---------------------------
def compute_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None

# ---------------------------
# PDF Processing
# ---------------------------
if st.session_state.pdf_text:
    placeholder = st.empty()
    new_hash = compute_text_hash(st.session_state.pdf_text)
    is_new_upload = new_hash != st.session_state.pdf_hash

    if is_new_upload:
        # Clear old embeddings (disk + session)
        with st.spinner("Preparing your document..."):
            placeholder.markdown("""
                <div class="teddy">
                    <img src="https://media.tenor.com/_lYNcVvfWO8AAAAd/robot-teddy.gif">
                    <p>🤖 New PDF detected — preparing document. Hang tight 💜</p>
                </div>
            """, unsafe_allow_html=True)
            time.sleep(1)

            # Clear all previous embeddings
            clear_all_collections()
            st.session_state.vectordb = None
            st.session_state.embeddings_ready = False
            st.session_state.chat_history = []

            # Create fresh embeddings
            vectordb, collection_name = create_embeddings(st.session_state.pdf_text)
            st.session_state.vectordb = vectordb
            st.session_state.collection_name = collection_name
            st.session_state.embeddings_ready = True
            st.session_state.pdf_hash = new_hash

        placeholder.empty()
    else:
        if not st.session_state.embeddings_ready:
            # Defensive: create embeddings if missing
            vectordb, collection_name = create_embeddings(st.session_state.pdf_text)
            st.session_state.vectordb = vectordb
            st.session_state.collection_name = collection_name
            st.session_state.embeddings_ready = True

# ---------------------------
# User input form
# ---------------------------
with st.form(key="top_form", clear_on_submit=False):
    st.markdown('<div class="top-input">', unsafe_allow_html=True)
    user_input = st.text_input("Write your query here and click Send...", key="user_input", label_visibility="collapsed")
    submit = st.form_submit_button("Send")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Handle query
# ---------------------------
if submit and user_input.strip():
    st.session_state.chat_history.insert(0, ("user", user_input.strip()))
    st.session_state.chat_history.insert(1, ("bot", "Generating answer..."))
    st.rerun()

placeholder_bot_index = None
for idx, (role, txt) in enumerate(st.session_state.chat_history):
    if role == "bot" and txt == "Generating answer...":
        placeholder_bot_index = idx
        break

if placeholder_bot_index is not None:
    loading_box = st.empty()
    messages = itertools.cycle([
        "🤖 Thinking deeply...",
        "⚡ Searching for the best answer...",
        "🧠 Analyzing your document...",
        "💭 Almost there..."
    ])
    for _ in range(6):
        loading_box.markdown(f"""
            <div class="teddy">
                <img src="https://media.tenor.com/_lYNcVvfWO8AAAAd/robot-teddy.gif">
                <p style="font-size:16px;">{next(messages)}</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(1.6)

    try:
        if st.session_state.vectordb is None:
            answer = "Embeddings not ready. Please upload a PDF first."
        else:
            answer, docs = ask_question(user_input, st.session_state.vectordb)
    except Exception as e:
        answer = f"Error while querying document: {e}"

    st.session_state.chat_history[placeholder_bot_index] = ("bot", answer)
    loading_box.empty()
    st.rerun()

# ---------------------------
# Render chat
# ---------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f'<div class="user-msg">You — {msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg">Bot — {msg}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Footer
# ---------------------------
st.markdown("""
<div class="footer">
    🤖 Powered by DocMind • Made with 💜 by Ayush Mishra ✨
</div>
""", unsafe_allow_html=True)
