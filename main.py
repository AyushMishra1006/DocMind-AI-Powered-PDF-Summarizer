import streamlit as st
from pdf_utils import upload_and_extract_pdf
from embeddings_utils import create_embeddings
from llm_utils import ask_question
import time
import itertools

# ---------------------------
# Page configuration
# ---------------------------
st.set_page_config(
    page_title="DocMind – PDF Q&A",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------
# CSS Styling (keeps your black/purple theme)
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

/* Main title */
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

/* Chat container */
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

/* User message (left) */
.user-msg {
    background-color: #a020f0;
    color: white;
    padding: 10px 14px;
    border-radius: 15px 15px 15px 0;
    max-width: 75%;
    align-self: flex-start;
    font-weight: bold;
    box-shadow: 0 4px 10px rgba(160,32,240,0.08);
}

/* Bot message (right) */
.bot-msg {
    background-color: #4b0082;
    color: white;
    padding: 12px 16px;
    border-radius: 15px 15px 0 15px;
    max-width: 75%;
    align-self: flex-end;
    font-weight: bold;
    border: 1px solid #a020f0;
    box-shadow: 0 4px 10px rgba(75,0,130,0.08);
}

/* Input at top container */
.top-input {
    width: 100%;
    max-width: 980px;
    margin: 10px auto;
    display:flex;
    gap:10px;
    align-items: center;
}

/* Input box */
.stTextInput>div>div>input {
    background-color: #d3d3d3;
    color: black;
    font-weight: bold;
    border-radius: 8px;
    padding: 12px;
    width: 100%;
    border: none;
}

/* Button */
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

/* Teddy / loading area */
.teddy {
    text-align: center;
    font-size: 18px;
    color: white;
    margin-top: 8px;
    margin-bottom: 8px;
}
.teddy img {
    width: 160px;
    animation: bounce 1.5s infinite;
}
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}

/* Footer */
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
# Sidebar: PDF Upload (with small placeholder at bottom)
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
# Main area title
# ---------------------------
st.markdown('<div class="main-title">🤖 DocMind – PDF Q&A Assistant</div>', unsafe_allow_html=True)

# ---------------------------
# Initialize chat history container
# ---------------------------
if "chat_history" not in st.session_state:
    # chat_history is a list of tuples (role, text)
    # newest exchanges will be inserted at the front so index 0 is the most recent.
    st.session_state.chat_history = []

# ---------------------------
# Top input form (ENTER will submit)
# ---------------------------
with st.form(key="top_form", clear_on_submit=False):
    st.markdown('<div class="top-input">', unsafe_allow_html=True)
    user_input = st.text_input("Write your query here and click Send...", key="user_input", label_visibility="collapsed")
    submit = st.form_submit_button("Send")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# PDF processing & Q&A
# ------------- answer--------------
# show loading teddy while embeddings get created (only once after upload)
if pdf_text:
    placeholder = st.empty()
    if "embeddings_ready" not in st.session_state:
        with st.spinner("Preparing your document..."):
            placeholder.markdown("""
                <div class="teddy">
                    <img src="https://media.tenor.com/_lYNcVvfWO8AAAAd/robot-teddy.gif">
                    <p>🤖 Your document is being prepared. Hang tight 💜</p>
                </div>
            """, unsafe_allow_html=True)
            time.sleep(2)  # simulate
            create_embeddings(pdf_text)
            st.session_state.embeddings_ready = True
        placeholder.empty()

    # ---------------------------
    # If user submitted, handle it
    # ---------------------------
    if submit and user_input and user_input.strip():
        # --- Add user message at the top ---
        st.session_state.chat_history.insert(0, ("user", user_input.strip()))
        # show an immediate loading bot placeholder below the user (index 1)
        st.session_state.chat_history.insert(1, ("bot", "Generating answer..."))

        # re-render (small immediate update)
        st.rerun()

    # If a previous run placed a "Generating answer..." placeholder at index 1,
    # we should detect it and actually compute the answer once per run.
    placeholder_bot_index = None
    if st.session_state.chat_history:
        # find a bot placeholder that equals "Generating answer..."
        for idx, (role, txt) in enumerate(st.session_state.chat_history):
            if role == "bot" and txt == "Generating answer...":
                placeholder_bot_index = idx
                break

    if placeholder_bot_index is not None:
        # Show loading UI near top while generating
        loading_box = st.empty()
        messages = itertools.cycle([
            "🤖 Thinking deeply...",
            "⚡ Searching for the best answer...",
            "🧠 Analyzing your document...",
            "💭 Almost there..."
        ])

        # slower rotation: show each message for 1.6 seconds
        for _ in range(6):
            loading_box.markdown(f"""
                <div class="teddy">
                    <img src="https://media.tenor.com/_lYNcVvfWO8AAAAd/robot-teddy.gif">
                    <p style="font-size:16px;">{next(messages)}</p>
                </div>
            """, unsafe_allow_html=True)
            time.sleep(1.6)

        from embeddings_utils import vectordb
        answer, docs = ask_question(user_input, vectordb)


        # replace the placeholder bot text with the real answer
        st.session_state.chat_history[placeholder_bot_index] = ("bot", answer)
        loading_box.empty()
        # re-render to show final answer
        st.rerun()

    # ---------------------------
    # Render chat (most recent first)
    # ---------------------------
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for role, msg in st.session_state.chat_history:
        if role == "user":
            st.markdown(f'<div class="user-msg">You — {msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-msg">Bot — {msg}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # No PDF yet
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
