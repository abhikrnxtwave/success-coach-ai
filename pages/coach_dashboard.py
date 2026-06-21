import streamlit as st
import pandas as pd

from services.signal_reader import (
    get_signals
)


from graphs.planning_graph import (
    run_planning_workflow
)



from graphs.brief_graph import (
    run_brief_workflow
)



# ----------------------------------
# Page Title
# ----------------------------------

st.set_page_config(
    page_title="Coach Dashboard",
    page_icon="🎓",
    layout="wide"
)

st.title(
    "🎓 Coach Dashboard"
)
# ----------------------------------
# Sidebar
# ----------------------------------

st.sidebar.title(
    "📅 Calendar Events"
)

# ----------------------------------
# Load Signals
# ----------------------------------

signals = get_signals()

if not signals:

    st.warning(
        "No signals found."
    )

    st.stop()

df = pd.DataFrame(signals)

# ----------------------------------
# Metrics
# ----------------------------------
critical_count = 0

critical_count = 0

for row in signals:

    severity = str(
        row.get(
            "severity",
            ""
        )
    ).upper()

    if "CRITICAL" in severity:

        critical_count += 1


planned_today = 0

if "today_plan" in st.session_state:

    planned_today = len(
    st.session_state.get(
        "today_plan",
        {}
    ).get(
        "planned_sessions",
        []
    )
)

col1, col2= st.columns(2)

with col1:

    st.metric(
        "🚨 Critical",
        critical_count
    )

with col2:

    st.metric(
        "📅 Planned Today",
        planned_today
    )



# ----------------------------------
# AI Daily Plan
# ----------------------------------

st.divider()

st.header(
    "📅 AI Daily Coaching Plan"
)

if st.button(
    "🚀 Generate Today's Plan",
    use_container_width=True
):

    plan = run_planning_workflow()

    st.session_state[
        "today_plan"
    ] = plan

    st.rerun()


# ----------------------------------
# Default Values
# ----------------------------------

planned_sessions = []
deferred_students = []
calendar_events = []


if "today_plan" in st.session_state:

    plan = st.session_state[
        "today_plan"
    ]

    planned_sessions = plan.get(
        "planned_sessions",
        []
    )

    deferred_students = plan.get(
        "deferred_students",
        []
    )

    calendar_events = plan.get(
        "calendar_events",
        []
    )



# ----------------------------------
# Sidebar Calendar Events
# ----------------------------------

if calendar_events:

    st.sidebar.success(
        f"{len(calendar_events)} Events Created"
    )

    for event in calendar_events:

        st.sidebar.markdown(
            f"""
### 📅 {event['title']}

🕘 {event['start_time']}

⏱ {event['duration']} mins
"""
        )

        if event.get(
            "event_link"
        ):

            st.sidebar.markdown(
                f"[Open Event]({event['event_link']})"
            )

        st.sidebar.divider()

else:

    st.sidebar.info(
        "Generate today's plan to create calendar events."
    )




# ----------------------------------
# Coach Schedule
# ----------------------------------

if "today_plan" in st.session_state:

    st.header(
        "🗓 Coach Schedule"
    )

    if not planned_sessions:

        st.info(
            "No students require coaching today."
        )

    else:

        for session in planned_sessions:

            with st.container(
                border=True
            ):

                st.markdown(
                    f"""
## 🕘 {session['time']}

### 👨‍🎓 {session['student_id']}

**🎯 Session Type:** {session['session_type']}

**⚠️ Severity:** {session['severity']}

**📌 Signal:** {session['signal_type']}

**⏱ Duration:** {session['duration']} mins
"""
                )

                student_id = session["student_id"]

                button_key = (
                    f"prepare_btn_{student_id}"
                )

                brief_key = (
                    f"brief_data_{student_id}"
                )

                if st.button(
                    "📄 Prepare For Session",
                    key=button_key
                ):

                    with st.spinner(
                        "Preparing coach brief..."
                    ):

                        brief = run_brief_workflow(
                            student_id
                        )

                        st.session_state[
                            brief_key
                        ] = brief

                if brief_key in st.session_state:

                    brief = st.session_state[
                        brief_key
                    ]

                    st.markdown(
    f"""
### 👤 Student Snapshot

{brief.get('student_snapshot', 'N/A')}

---

### 📝 Last Conversation Summary

{brief.get('last_conversation_summary', 'N/A')}

---

### 💬 What Was Discussed

{brief.get('what_was_discussed', 'N/A')}

---

### ✅ Decisions & Recommendations

{brief.get('decisions_and_recommendations', 'N/A')}

---

### 🎯 Follow-Up Topics For Today

{brief.get('follow_up_topics', 'N/A')}
"""
)

                    st.divider()

    
    # -------------------------
    # Deferred Students
    # -------------------------

    st.subheader(
        "⏳ Deferred To Tomorrow"
    )

    if not deferred_students:

        st.success(
            "No deferred students."
        )

    else:

        for student in deferred_students:

            with st.container(
                border=True
            ):

                st.warning(
                    f"""
👨‍🎓 {student['student_id']}

Reason:
{student['reason']}
"""
                )

# ----------------------------------
# Critical Signals
# ----------------------------------

st.divider()

st.header(
    "🚨 Critical Signals"
)

critical_found = False

for row in signals:

    severity = (
        row.get(
            "severity",
            ""
        ).upper()
    )

    if "CRITICAL" in severity:

        critical_found = True

        with st.expander(
            f"{row.get('student_id')} | {row.get('signal_type')}"
        ):

            st.write(
                f"Severity: {row.get('severity')}"
            )

            st.write(
                f"Urgency: {row.get('urgency')}"
            )

            st.write(
                f"Action Status: {row.get('actioned')}"
            )

            st.write(
                row.get(
                    "reason",
                    ""
                )
            )

if not critical_found:

    st.success(
        "No critical signals."
    )