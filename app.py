import streamlit as st

from config.llm import get_ai_response
from utils.prompts import SYSTEM_PROMPT

from services.agent import run_agent
from services.student_service import get_all_students


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

    student_names = get_all_students()

    selected_student = st.selectbox(
        "Select Student",
        student_names,
        key="student_selector"
    )

    if "current_student" not in st.session_state:
        st.session_state.current_student = selected_student

    if selected_student != st.session_state.current_student:

        st.session_state.messages = []

        st.session_state.current_student = (
            selected_student
        )

        st.rerun()

    st.divider()

    st.info("""
        Ask questions about:

        • Student Performance
        • Attendance
        • Scores
        • Upcoming Exams
        • Subject Concepts
        • General Knowledge
        """)

# -------------------------
# Session State
# -------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------
# Chat History
# -------------------------

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------
# User Input
# -------------------------

prompt = st.chat_input(
    "💬 Ask me anything..."
)

if prompt:

    # -------------------------
    # Save User Message
    # -------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # -------------------------
    # Show User Message
    # -------------------------

    with st.chat_message("user"):
        st.markdown(prompt)

    # -------------------------
    # Assistant Response
    # -------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            # -------------------------
            # Agent decides tools
            # -------------------------

            agent_result = run_agent(
                prompt,
                selected_student
            )

            student_context = (
                agent_result["student_context"]
            )

            knowledge_context = (
                agent_result["knowledge_context"]
            )

            tool_decision = (
                agent_result["decision"]
            )

            # -------------------------
            # Build Messages
            # -------------------------

            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ]

            # -------------------------
            # Student Context
            # -------------------------

            if student_context:

                messages.append(
                    {
                        "role": "system",
                        "content": student_context
                    }
                )

            # -------------------------
            # Knowledge Context
            # -------------------------

            if knowledge_context:

                messages.append(
                    {
                        "role": "system",
                        "content": f"""
Knowledge Base Context:

{knowledge_context}

Instructions:

- Use the knowledge base context for study-related questions.
- Prefer knowledge base information over general knowledge.
- If the context is not relevant, answer normally.
"""
                    }
                )

            # -------------------------
            # Chat History
            # -------------------------

            messages.extend(
                st.session_state.messages
            )

            # -------------------------
            # Generate Response
            # -------------------------

            response = get_ai_response(
                messages
            )

            st.markdown(response)

    # -------------------------
    # Save Assistant Message
    # -------------------------

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