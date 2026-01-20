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
    --accent: #b84dff;
    --accent-strong: #9b2cff;
    --accent-dark: #5a189a;

    --accent-gradient: linear-gradient(
        135deg,
        #3a0ca3,
        #7209b7,
        #b5179e,
        #f72585
    );

    --accent-soft: rgba(184,77,255,0.35);
    --accent-glow: 0 0 25px rgba(184,77,255,0.6);

    --bg-main: #000000;
    --bg-soft: #0b0614;
    --bg-widget: #12081f;
    --border-soft: rgba(255,255,255,0.12);
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

/* ============================
   SEARCH BOX (FILLED GRADIENT)
============================= */
div[data-testid="stTextInput"] input {
    background: linear-gradient(135deg, #1a002b, #2a004f) !important;
    color: white !important;
    border-radius: 14px !important;
    border: 1.5px solid transparent !important;
    padding: 12px 14px !important;
    background-clip: padding-box;
    box-shadow: 0 0 18px rgba(183,23,158,0.45) !important;
    transition: all 0.15s ease-in-out;
}

div[data-testid="stTextInput"] input::placeholder {
    color: rgba(255,255,255,0.65) !important;
}

div[data-testid="stTextInput"] input:focus {
    background: linear-gradient(135deg, #2a004f, #3a006f) !important;
    border: 1.5px solid var(--accent) !important;
    box-shadow: 0 0 30px rgba(183,23,158,0.8) !important;
    outline: none !important;
}

/* ============================
   TITLE (FILLED + SMOOTH)
============================= */
.main-title {
    position: relative;
    overflow: visible;

    background: linear-gradient(
        180deg,
        #1c0f3a,
        #2a1554
    );
    border-radius: 16px;
    padding: 20px 22px;
    font-size: 38px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 30px;

    color: #ffffff;
    letter-spacing: 0.6px;
    text-shadow:
        0 0 6px rgba(184,77,255,0.45),
        0 0 14px rgba(184,77,255,0.25);

    border: 1px solid rgba(184,77,255,0.65);

    box-shadow:
        0 0 0 1px rgba(184,77,255,0.25),
        0 16px 45px rgba(0,0,0,0.7),
        inset 0 0 24px rgba(255,255,255,0.08);
}

.main-title::before {
    content: "";
    position: absolute;
    inset: -30px;
    background: radial-gradient(
        circle,
        rgba(184,77,255,0.45),
        rgba(184,77,255,0.2),
        transparent 70%
    );
    filter: blur(45px);
    z-index: -1;
}






@keyframes waveIn {
    0% { opacity: 0; transform: translateY(30px); }
    100% { opacity: 1; transform: translateY(0); }
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
    padding: 12px 16px;
    border-radius: 14px;
    max-width: 75%;
    margin-bottom: 8px;
}

.bot-msg {
    background: #101010;
    padding: 14px 18px;
    border-radius: 14px;
    max-width: 75%;
    margin-bottom: 8px;
}

.suggestion-box,
.user-msg,
.bot-msg {
    border-width: 2px;
    border-style: solid;
    border-image: var(--accent-gradient) 1;
}

/* BUTTON HOVER */
button:hover,
div[data-testid="stButton"] > button:hover {
    background: var(--accent-gradient) !important;
    color: white !important;
    box-shadow: var(--accent-glow) !important;
    transform: scale(1.05);
    transition: all 0.15s ease-in-out;
}

.chat-container {
    max-height: calc(100vh - 180px);
    overflow-y: auto;
    padding-bottom: 120px;
}

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

footer {
    display: none;
}
            /* =========================================================
   FORCE DARK MODE (PREVENT LIGHT THEME OVERRIDE)
========================================================= */
html, body, .stApp {
    color-scheme: dark !important;
}

/* Fix SEND button turning white in light mode */
button,
div[data-testid="stButton"] > button {
    background: #121212 !important;
    color: #ffffff !important;
    border: 1px solid var(--accent) !important;
}

/* Fix suggestion buttons / suggestion boxes */
.suggestion-box,
.suggestion-box * {
    background: #0f0f0f !important;
    color: #ffffff !important;
}

/* Fix Streamlit auto light-mode inputs */
input, textarea {
    background-color: #121212 !important;
    color: #ffffff !important;
}

/* Fix hover still staying dark */
button:hover,
div[data-testid="stButton"] > button:hover {
    background: var(--accent-gradient) !important;
    color: white !important;
}

/* Prevent browser forced light styles */
@media (prefers-color-scheme: light) {
    * {
        color-scheme: dark !important;
    }
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
    

# -------------------------------------------------
# CENTRALIZED ANSWER GENERATION (FIXED)
# -------------------------------------------------
if st.session_state.event_question and not st.session_state.is_thinking:
    st.session_state.is_thinking = True

    q = st.session_state.event_question

    # add user message
    st.session_state.chat_history.append(("user", q))

    # add thinking placeholder
    thinking_index = len(st.session_state.chat_history)
    st.session_state.chat_history.append(("bot", "🤖 Thinking… preparing answer…"))

    # generate answer
    answer, _ = ask_question(q, st.session_state.vectordb)

    # replace thinking message (CORRECT INDEX)
    st.session_state.chat_history[thinking_index] = ("bot", answer)

    # reset flags
    st.session_state.event_question = None
    st.session_state.is_thinking = False

    st.rerun()


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
