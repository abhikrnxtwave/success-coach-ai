import streamlit as st
import pandas as pd

from services.signal_reader import (
    get_signals
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
high_count = 0
pending_count = 0

for row in signals:

    severity = (
        row.get(
            "severity",
            ""
        ).upper()
    )

    actioned = (
        row.get(
            "actioned",
            ""
        )
    )

    if "CRITICAL" in severity:

        critical_count += 1

    elif "HIGH" in severity:

        high_count += 1

    if actioned != "Done":

        pending_count += 1

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "🚨 Critical",
        critical_count
    )

with col2:

    st.metric(
        "⚠️ High",
        high_count
    )

with col3:

    st.metric(
        "📋 Pending",
        pending_count
    )

# ----------------------------------
# Full Signal Table
# ----------------------------------

# st.divider()

# st.subheader(
#     "📊 All Signals"
# )

# st.dataframe(
#     df,
#     use_container_width=True
# )

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
# High Priority Signals
# ----------------------------------

st.divider()

st.header(
    "⚠️ High Priority Signals"
)

high_found = False

for row in signals:

    severity = (
        row.get(
            "severity",
            ""
        ).upper()
    )

    if "HIGH" in severity:

        high_found = True

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

if not high_found:

    st.success(
        "No high priority signals."
    )

# ----------------------------------
# Requires Action Today
# ----------------------------------

st.divider()

st.header(
    "⏰ Requires Action Today"
)

today_found = False

for row in signals:

    urgency = (
        row.get(
            "urgency",
            ""
        ).upper()
    )

    if "TODAY" in urgency:

        today_found = True

        st.error(
            f"{row.get('student_id')} | {row.get('signal_type')}"
        )

if not today_found:

    st.success(
        "No urgent follow-ups today."
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

# ----------------------------------
# Pending Follow-Ups
# ----------------------------------

st.divider()

st.header(
    "📋 Pending Follow-Ups"
)

pending_found = False

for row in signals:

    actioned = (
        row.get(
            "actioned",
            ""
        )
    )

    if actioned != "Done":

        pending_found = True

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
                f"Current Status: {actioned}"
            )

            st.write(
                row.get(
                    "reason",
                    ""
                )
            )

if not pending_found:

    st.success(
        "No pending follow-ups."
    )