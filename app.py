import streamlit as st

from config.llm import get_ai_response
from utils.prompts import SYSTEM_PROMPT

from services.student_service import (
    get_all_students,
    get_student_profile
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
        st.session_state.current_student = selected_student

        st.rerun()

    st.divider()

    st.info(
        """
        Ask questions about:
        - Student Performance
        - Attendance
        - Scores
        - Upcoming Exams
        - General Knowledge
        """
    )
# -------------------------
# Session State
# -------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

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

    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            student_profile = get_student_profile(
                selected_student
            )

            # -------------------------
            # Scores
            # -------------------------

            scores_text = ""

            for score in student_profile["scores"]:

                scores_text += (
                    f"{score['subject']}: "
                    f"{score['score']}/{score['max_score']} "
                    f"(Date: {score['date']})\n"
                )

            # -------------------------
            # Latest Attendance
            # -------------------------

            attendance_records = student_profile["attendance"]

            total_classes_scheduled = sum(
                int(row["classes_scheduled"])
                for row in attendance_records
            )

            total_classes_attended = sum(
                int(row["classes_attended"])
                for row in attendance_records
            )

            avg_attendance_pct = 0

            if total_classes_scheduled > 0:
                avg_attendance_pct = round(
                    (total_classes_attended / total_classes_scheduled) * 100,
                    2
                )

            # -------------------------
            # Upcoming Exams
            # -------------------------

            exam_text = ""

            for exam in student_profile["exams"]:

                exam_text += (
                    f"{exam['subject']} | "
                    f"{exam['exam_type']} | "
                    f"{exam['exam_date']}\n"
                )

            # -------------------------
            # Student Context
            # -------------------------

            student_context = f"""
Selected Student

Name:
{student_profile['student']['name']}

Program:
{student_profile['student']['program']}

Cohort:
{student_profile['student']['cohort']}

Attendance Summary

Classes Attended:
{total_classes_attended}

Classes Scheduled:
{total_classes_scheduled}

Average Attendance:
{avg_attendance_pct}%

Exam Scores:
{scores_text}

Upcoming Exams:
{exam_text}

When discussing attendance:
mention both the number of classes attended and scheduled,
along with the average attendance percentage.

Use student data whenever relevant.
For general knowledge questions, answer normally.
"""

            # -------------------------
            # Build Messages
            # -------------------------

            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "system",
                    "content": student_context
                }
            ]

            messages.extend(
                st.session_state.messages
            )

            response = get_ai_response(
                messages
            )

            st.markdown(response)

    # Save assistant response
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