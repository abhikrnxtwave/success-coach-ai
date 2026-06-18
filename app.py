import streamlit as st

from config.llm import get_ai_response
from utils.prompts import SYSTEM_PROMPT

# -------------------------
# Page Config
# -------------------------

st.set_page_config(
    page_title="Student Success AI",
    page_icon="🎓",
    layout="wide"
)

# -------------------------
# Custom CSS
# -------------------------

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.hero {
    text-align: center;
    padding: 20px;
    border-radius: 15px;
    background: linear-gradient(
        135deg,
        #4F46E5,
        #7C3AED
    );
    color: white;
    margin-bottom: 20px;
}

.hero h1 {
    margin-bottom: 5px;
}

.hero p {
    font-size: 18px;
    opacity: 0.9;
}

.footer {
    text-align: center;
    color: gray;
    padding-top: 20px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# Header
# -------------------------

st.markdown("""
<div class="hero">
    <h1>🎓 Student Success AI</h1>
    <p>Your personal AI learning coach</p>
</div>
""", unsafe_allow_html=True)

# -------------------------
# Sidebar
# -------------------------

with st.sidebar:
    st.header("📚 Learning Assistant")

    st.info(
        """
        Ask questions about:
        - Programming
        - Science
        - Mathematics
        - Career Guidance
        - Study Tips
        """
    )

# -------------------------
# Session State
# -------------------------

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

# -------------------------
# Chat History
# -------------------------

for msg in st.session_state.messages:

    if msg["role"] == "system":
        continue

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------
# User Input
# -------------------------

prompt = st.chat_input(
    "💬 Ask me anything..."
)

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            response = get_ai_response(
                st.session_state.messages
            )

            st.markdown(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

# -------------------------
# Footer
# -------------------------

st.markdown("""
<div class="footer">
    Student Success AI
</div>
""", unsafe_allow_html=True)