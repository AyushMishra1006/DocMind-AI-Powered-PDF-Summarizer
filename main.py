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
# GLOBAL CSS (LOCKED DARK THEME + UPLOADER FIX + ANIMATION)
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

.stApp {
    background-color: black !important;
    background-image:
        radial-gradient(circle at top, rgba(255,255,255,0.08), transparent 40%),
        url("https://www.transparenttextures.com/patterns/stardust.png");
    background-size: cover;
    color: var(--text-main) !important;
}

header, .stToolbar {
    background: black !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] {
    background: #0b0b0b !important;
    border-right: 1px solid var(--border-soft);
}

[data-testid="stFileUploader"] {
    background: #0f0f0f !important;
    border-radius: 14px !important;
    border: 1.5px solid var(--accent) !important;
    box-shadow: 0 0 14px var(--accent-soft);
}

[data-testid="stFileUploader"] section {
    background: #0f0f0f !important;
}

[data-testid="stFileUploader"] * {
    color: #ffffff !important;
}

[data-testid="stFileUploader"] button {
    background: #121212 !important;
    color: #ffffff !important;
    border: 1px solid var(--accent) !important;
    border-radius: 999px !important;
}

input, textarea {
    background-color: var(--bg-widget) !important;
    color: var(--text-main) !important;
    border-radius: 10px !important;
    border: 1px solid var(--border-soft) !important;
}

button {
    background-color: var(--bg-widget) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 999px !important;
    padding: 10px 18px !important;
    font-weight: 600;
}

@keyframes waveIn {
    0% { opacity: 0; transform: translateY(30px); }
    100% { opacity: 1; transform: translateY(0); }
}

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
    animation: waveIn 0.9s ease-out forwards;
}

div[data-testid="stForm"] {
    animation: waveIn 1.2s ease-out forwards;
    animation-delay: 0.25s;
    opacity: 0;
}

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

.suggestion-box {
    margin-top: 14px;
    padding: 16px;
    border-radius: 14px;
    background: #0f0f0f;
    border: 1px solid var(--border-soft);
}

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

.footer {
    text-align: center;
    color: #bbbbbb;
    font-weight: 600;
    margin-top: 30px;
    padding: 15px;
}
/* ============================
   BUTTON HOVER EFFECT (PURPLE)
============================= */
button:hover,
div[data-testid="stButton"] > button:hover {
    background: var(--accent) !important;
    color: black !important;
    box-shadow: 0 0 16px var(--accent) !important;
    transform: scale(1.04);
    transition: all 0.15s ease-in-out;
}
            
/* ============================
   SEARCH BOX PURPLE FOCUS
============================= */
div[data-testid="stTextInput"] input:focus {
    border: 2px solid var(--accent) !important;
    box-shadow: 0 0 18px var(--accent-soft) !important;
    outline: none !important;
}
input, textarea {
    transition: all 0.15s ease-in-out;
}
div[data-testid="stTextInput"] input:not(:placeholder-shown) {
    box-shadow: 0 0 16px var(--accent-soft) !important;
    border: 1.5px solid var(--accent) !important;
}
.chat-container {
    max-height: calc(100vh - 180px);
    overflow-y: auto;
    padding-bottom: 120px;
}

/* sticky input bar */
.input-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #000000;
    padding: 16px 24px;
    border-top: 1px solid rgba(255,255,255,0.1);
    z-index: 999;
}

/* prevent footer overlap */
footer {
    display: none;
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
if "event_question" not in st.session_state:
    st.session_state.event_question = None
if "is_thinking" not in st.session_state:
    st.session_state.is_thinking = False
if "show_input" not in st.session_state:
    st.session_state.show_input = True


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
# SUGGESTED QUESTIONS
# -------------------------------------------------
if st.session_state.suggested_questions:
    st.markdown('<div class="suggestion-box">', unsafe_allow_html=True)
    st.markdown("### 💡 Suggested Questions")

    col1, col2 = st.columns(2)
    for i, q in enumerate(st.session_state.suggested_questions):
        with (col1 if i % 2 == 0 else col2):
            if st.button(q, key=f"suggest_{i}"):
                st.session_state.show_input = True
                st.session_state.event_question = q
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# CHAT RENDER
# -------------------------------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

if document_text:
    for role, msg in st.session_state.chat_history:
        css = "user-msg" if role == "user" else "bot-msg"
        st.markdown(f'<div class="{css}">{msg}</div>', unsafe_allow_html=True)
else:
    st.info("📄 Upload a document to get started")

st.markdown("</div>", unsafe_allow_html=True)




# -------------------------------------------------
# FIXED INPUT BAR (CHATGPT STYLE)
# -------------------------------------------------
submitted = False
user_question = None
st.markdown('<div class="input-bar">', unsafe_allow_html=True)

if st.session_state.show_input:
    with st.form("question_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])

        with col1:
            user_question = st.text_input(
                "Ask a question about the document",
                label_visibility="collapsed"
            )

        with col2:
            submitted = st.form_submit_button("Send")
else:
    submitted = False
    user_question = None

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# SUBMIT HANDLER
# -------------------------------------------------
if submitted and user_question:
    st.session_state.event_question = user_question
    st.rerun()

# -------------------------------------------------
# CENTRALIZED ANSWER GENERATION (SINGLE SOURCE)
# -------------------------------------------------
if st.session_state.event_question:
    q = st.session_state.event_question

    # insert user message
    st.session_state.chat_history.append(("user", q))

    # insert thinking message ABOVE it
    st.session_state.chat_history.append(("bot", "🤖 Thinking… preparing answer…"))

    answer, _ = ask_question(q, st.session_state.vectordb)

    # replace the thinking message (index 0)
    st.session_state.chat_history[0] = ("bot", answer)


    st.session_state.event_question = None

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
