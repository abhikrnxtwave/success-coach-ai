import streamlit as st
import pandas as pd

from services.signal_reader import (
    get_signals
)


from graphs.planning_graph import (
    run_planning_workflow,
    resolve_critical_conflict
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
# Default Values
# ----------------------------------

planned_sessions = []
deferred_students = []
calendar_events = []
plan_summary = []
critical_conflicts = []


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

    plan_summary = plan.get(
        "plan_summary",
        []
    )

    critical_conflicts = plan.get(
        "critical_conflicts",
        []
    )


# ----------------------------------
# Plan Updates
# (top of dashboard — coach sees what
#  changed before opening anything else)
# ----------------------------------

if plan_summary:

    st.header("🔄 Plan Updates")

    for item in plan_summary:

        message = item.get(
            "message",
            item.get("reason", "")
        )

        item_type = item.get("type")

        if item_type == "NEW_SERIOUS_CONCERN":

            st.error(f"🚨 {message}")

        elif item_type == "MOVED_TO_TOMORROW":

            st.warning(f"⏳ {message}")

        elif item_type == "DEFERRED":

            st.info(f"📅 {message}")

        elif item_type == "RESCHEDULED":

            st.info(f"🔁 {message}")

        elif item_type == "COACH_DECISION_REQUIRED":

            st.error(f"⚠️ {message}")

        elif item_type == "COACH_DECISION_MADE":

            st.success(f"✅ {message}")

        else:

            st.info(message)

    st.divider()


# ----------------------------------
# Coach Decision Required
# (Scenario 3 — biggest M9 feature)
# ----------------------------------

if critical_conflicts:

    st.header("⚠️ Coach Decision Required")

    if len(critical_conflicts) == 1:

        st.warning(
            "A CRITICAL student needs coaching but today's capacity is full. "
            "Please decide how to proceed."
        )

    else:

        st.warning(
            "Multiple CRITICAL students need coaching but only limited capacity "
            "remains today. Please decide who should be prioritized."
        )

    for student in critical_conflicts:

        with st.container(border=True):

            st.markdown(
                f"""
### 👨‍🎓 {student['student_id']}

Severity:
{student['severity']}

Signal:
{student['signal_type']}

Reason:
{student['reason']}
"""
            )

            schedule_key = (
                f"schedule_btn_{student['student_id']}"
            )

            if st.button(
                f"Schedule {student['student_id']}",
                key=schedule_key
            ):

                others = [
                    s for s in critical_conflicts
                    if s["student_id"] != student["student_id"]
                ]

                (
                    scheduled_session,
                    event,
                    newly_deferred,
                    summary_item
                ) = resolve_critical_conflict(
                    student,
                    others
                )

                updated_plan = st.session_state.get(
                    "today_plan",
                    {}
                )

                updated_plan["planned_sessions"] = (
                    updated_plan.get("planned_sessions", [])
                    + [scheduled_session]
                )

                updated_plan["calendar_events"] = (
                    updated_plan.get("calendar_events", [])
                    + [event]
                )

                updated_plan["deferred_students"] = (
                    updated_plan.get("deferred_students", [])
                    + newly_deferred
                )

                updated_plan["plan_summary"] = (
                    updated_plan.get("plan_summary", [])
                    + [summary_item]
                )

                updated_plan["critical_conflicts"] = []

                st.session_state["today_plan"] = updated_plan

                st.rerun()

    st.divider()


# ----------------------------------
# AI Daily Plan
# ----------------------------------

st.header(
    "📅 AI Daily Coaching Plan"
)

if st.button(
    "🚀 Generate Today's Plan",
    use_container_width=True
):

    previous_sessions = st.session_state.get(
        "today_plan",
        {}
    ).get(
        "planned_sessions",
        []
    )

    plan = run_planning_workflow(
        previous_sessions=previous_sessions
    )

    st.session_state[
        "today_plan"
    ] = plan

    st.rerun()


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