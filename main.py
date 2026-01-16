import streamlit as st
import hashlib
import time

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
# GLOBAL CSS (UI MASTER STYLE)
# -------------------------------------------------
st.markdown("""
<style>
:root {
    --accent: #a020f0;
    --accent-soft: rgba(160,32,240,0.35);
    --bg-main: #000;
    --bg-soft: #0f0f0f;
    --bg-widget: #121212;
    --border-soft: rgba(255,255,255,0.15);
    --text-main: #fff;
    --text-muted: #ccc;
}

/* ===================== */
/* BACKGROUND + STARS */
/* ===================== */
.stApp {
    background-color: black !important;
    background-image:
        radial-gradient(circle at top, rgba(255,255,255,0.07), transparent 40%),
        url("https://www.transparenttextures.com/patterns/stardust.png");
    animation: starsMove 120s linear infinite;
}

@keyframes starsMove {
    from { background-position: 0 0; }
    to { background-position: 10000px 10000px; }
}

/* Remove top bar */
header, .stToolbar { display: none !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0b0b0b !important;
    border-right: 1px solid var(--border-soft);
}

/* ===================== */
/* FILE UPLOADER */
/* ===================== */
[data-testid="stFileUploader"] {
    background: #0f0f0f !important;
    border-radius: 14px !important;
    border: 1.5px solid var(--accent) !important;
    box-shadow: 0 0 14px var(--accent-soft);
}
[data-testid="stFileUploader"] * {
    color: white !important;
}

/* ===================== */
/* INPUT INLINE SEND */
/* ===================== */
.inline-form {
    display: flex;
    gap: 10px;
    align-items: center;
}
.inline-form input {
    flex: 1;
}
.inline-form button {
    height: 44px;
}

/* ===================== */
/* BUTTONS */
/* ===================== */
button {
    background: #121212 !important;
    color: white !important;
    border: 1px solid var(--accent) !important;
    border-radius: 999px !important;
    font-weight: 600;
}
button:hover {
    background: var(--accent) !important;
    color: black !important;
}

/* ===================== */
/* WAVE LOAD */
/* ===================== */
@keyframes waveIn {
    from { opacity: 0; transform: translateY(25px); }
    to { opacity: 1; transform: translateY(0); }
}

.main-title {
    animation: waveIn 0.9s ease-out forwards;
    background: #0f0f0f;
    border: 1px solid var(--accent);
    box-shadow: 0 0 18px var(--accent-soft);
    border-radius: 14px;
    padding: 14px;
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 24px;
}

/* ===================== */
/* SKELETON LOADER */
/* ===================== */
.skeleton {
    height: 18px;
    border-radius: 6px;
    background: linear-gradient(
        90deg,
        #111 25%,
        #222 37%,
        #111 63%
    );
    animation: shimmer 1.4s infinite;
}
@keyframes shimmer {
    0% { background-position: -200px 0; }
    100% { background-position: 200px 0; }
}

/* ===================== */
/* TYPING DOTS */
/* ===================== */
.typing::after {
    content: " .";
    animation: dots 1.4s steps(3, end) infinite;
}
@keyframes dots {
    0% { content: " ."; }
    33% { content: " .."; }
    66% { content: " ..."; }
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
    color: #bbb;
    font-weight: 600;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.header("📄 Upload Document")
document_text = upload_and_extract_file()

st.sidebar.markdown("""
<div style="font-family:monospace; padding:14px; background:#0f0f0f; border-radius:12px;">
▸ STATUS : READY<br>
▸ MODE : DOCUMENT INTELLIGENCE<br>
▸ INPUT : PDF / IMAGE<br>
▸ ENGINE : OCR + GEMINI<br>
▸ STATE : AWAITING QUERY
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# TITLE
# -------------------------------------------------
st.markdown('<div class="main-title">🤖 DocMind – Document Intelligence Assistant</div>', unsafe_allow_html=True)

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
for k in ["chat_history", "vectordb", "doc_hash", "suggested_questions"]:
    st.session_state.setdefault(k, [] if k == "chat_history" else None)

# -------------------------------------------------
# HASH
# -------------------------------------------------
def compute_hash(text):
    return hashlib.sha256(text.encode()).hexdigest() if text else None

current_hash = compute_hash(document_text)
is_new_upload = current_hash and current_hash != st.session_state.doc_hash

# -------------------------------------------------
# PROCESS DOCUMENT
# -------------------------------------------------
if is_new_upload:
    st.session_state.chat_history.clear()
    st.session_state.doc_hash = current_hash
    st.session_state.vectordb = None
    st.session_state.suggested_questions = []

    with st.spinner("📄 Processing document..."):
        time.sleep(0.4)
        st.markdown('<div class="skeleton"></div>', unsafe_allow_html=True)

        st.session_state.vectordb = create_embeddings(
            document_text,
            collection_name=f"docmind_{current_hash[:8]}",
            persist_dir=None
        )
        st.session_state.suggested_questions = generate_smart_questions(document_text, 4)

# -------------------------------------------------
# INLINE INPUT + SEND
# -------------------------------------------------
with st.form("inline_form", clear_on_submit=True):
    st.markdown('<div class="inline-form">', unsafe_allow_html=True)
    user_question = st.text_input("Ask a question about the document", label_visibility="collapsed")
    send = st.form_submit_button("Send")
    st.markdown('</div>', unsafe_allow_html=True)

if send and user_question:
    st.session_state.chat_history.insert(0, ("user", user_question))
    st.session_state.chat_history.insert(1, ("bot", "Thinking"))
    st.rerun()

# -------------------------------------------------
# ANSWER
# -------------------------------------------------
if st.session_state.chat_history:
    role, msg = st.session_state.chat_history[0]
    if role == "bot" and msg == "Thinking":
        with st.spinner("🤖"):
            answer, _ = ask_question(st.session_state.chat_history[1][1], st.session_state.vectordb)
        st.session_state.chat_history[0] = ("bot", answer)
        st.rerun()

# -------------------------------------------------
# CHAT RENDER
# -------------------------------------------------
if document_text:
    for role, msg in st.session_state.chat_history:
        css = "user-msg" if role == "user" else "bot-msg"
        if msg == "Thinking":
            msg = '<span class="typing">Thinking</span>'
        st.markdown(f'<div class="{css}">{msg}</div>', unsafe_allow_html=True)
else:
    st.info("📄 Upload a document to get started")

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown('<div class="footer">🤖 Powered by DocMind • Built by Ayush Mishra ✨</div>', unsafe_allow_html=True)
