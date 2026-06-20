import streamlit as st

from config.llm import get_ai_response
from utils.prompts import SYSTEM_PROMPT

from services.agent import run_agent
from services.student_service import get_all_students

from services.memory_summarizer import (
    generate_memory_objects
)

from utils.memory_parser import (
    split_memory
)

from tools.memory_tool import (
    save_memory,
    search_memory
)

from graphs.signal_graph import (
    run_signal_workflow
)

# -------------------------
# Page Config
# -------------------------

st.set_page_config(
    page_title="Student Success AI",
    page_icon="🎓",
    layout="wide"
)



# -------------------------
# Memory Save Notification
# -------------------------

if "memory_saved" not in st.session_state:
    st.session_state.memory_saved = False

if st.session_state.get("memory_saved"):

    st.success(
        "✅ Session saved to memory."
    )

    st.session_state.memory_saved = False
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

    st.divider()

    if st.button(
        "End Session"
    ):

        if st.session_state.messages:

            conversation_text = ""

            for msg in st.session_state.messages:

                conversation_text += (
                    f"{msg['role']}: "
                    f"{msg['content']}\n\n"
                )

            memory_text = generate_memory_objects(
                conversation_text
            )

            facts, summary = split_memory(
                memory_text
            )

            save_memory(
                student_id=selected_student,
                factual_memory=facts,
                session_summary=summary
            )

            historical_memory = search_memory(
                query=summary,
                student_id=selected_student
            )

            # -------------------------
            # Signal Detection
            # -------------------------

            signal_result = run_signal_workflow(
                student_id=selected_student,
                session_summary=summary,
                memory_context=historical_memory
            )

            ## print(signal_result) // printing signal result

            st.session_state.latest_signal = signal_result
            

            st.session_state.messages = []
            st.session_state.memory_saved = True

            st.rerun()
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

            memory_context = (
                agent_result["memory_context"]
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
            # Student Context

            if student_context:

                messages.append(
                    {
                        "role": "system",
                        "content": student_context
                    }
                )

            # Knowledge Context
            
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

            if memory_context:

                messages.append(
                    {
                        "role": "system",
                        "content": f"""
            Student Historical Memory:

            {memory_context}

            IMPORTANT:

            - These memories belong to the currently selected student.
            - Use them as factual context.
            - If the user asks about hobbies, goals,
            preferences, struggles, progress,
            previous discussions or habits,
            answer using these memories.
            - Do not say you do not know if the answer
            exists in the memories.
            - Do not mention memory retrieval.
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