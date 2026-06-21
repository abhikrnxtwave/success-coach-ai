import streamlit as st
import pandas as pd

from services.signal_reader import (
    get_signals
)


from graphs.planning_graph import (
    run_planning_workflow
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
manager_alerts = 0

for row in signals:

    severity = str(
        row.get(
            "severity",
            ""
        )
    ).upper()

    actioned = str(
        row.get(
            "actioned",
            ""
        )
    )

    if "CRITICAL" in severity:

        critical_count += 1

    if actioned == "Manager Notified":

        manager_alerts += 1

planned_today = 0

if "today_plan" in st.session_state:

    planned_today = len(
        st.session_state[
            "today_plan"
        ].get(
            "planned_sessions",
            []
        )
    )

col1, col2, col3 = st.columns(3)

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

with col3:

    st.metric(
        "🔴 Manager Alerts",
        manager_alerts
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

    st.subheader(
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

                st.info(
                    session["reason"]
                )

    st.divider()

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

# ----------------------------------
# Manager Alerts
# ----------------------------------

st.divider()

st.header(
    "🔴 Manager Alerts"
)

manager_found = False

for row in signals:

    actioned = (
        row.get(
            "actioned",
            ""
        )
    )

    if actioned == "Manager Notified":

        manager_found = True

        st.warning(
            f"{row.get('student_id')} requires manager attention"
        )

        with st.expander(
            "View Details"
        ):

            st.write(
                f"Signal Type: {row.get('signal_type')}"
            )

            st.write(
                f"Severity: {row.get('severity')}"
            )

            st.write(
                f"Urgency: {row.get('urgency')}"
            )

            st.write(
                row.get(
                    "reason",
                    ""
                )
            )

if not manager_found:

    st.success(
        "No manager alerts."
    )
