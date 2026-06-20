from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    END
)

from services.signal_agents import (
    detect_signal,
    assess_signal,
    decide_action
)

from services.escalation_agent import (
    generate_escalation_summary
)

from services.signal_service import (
    save_signal
)


# -----------------------------------
# State
# -----------------------------------

class SignalState(TypedDict):

    student_id: str

    session_summary: str

    memory_context: str

    signal_type: str

    assessment: dict

    decision: dict

    escalation_summary: str


# -----------------------------------
# Node 1
# -----------------------------------

def signal_detector_node(state):

    state["signal_type"] = detect_signal(
        state["session_summary"]
    )

    return state


# -----------------------------------
# Node 2
# -----------------------------------

def assessment_node(state):

    assessment = assess_signal(
        state["session_summary"],
        state["memory_context"],
        state["signal_type"]
    )

    # safety fallback
    if not isinstance(assessment, dict):

        assessment = {
            "severity": "LOW",
            "reason": str(assessment)
        }

    state["assessment"] = assessment

    return state


# -----------------------------------
# Node 3
# -----------------------------------

def decision_node(state):

    state["decision"] = decide_action(
        state["session_summary"],
        state["memory_context"],
        state["signal_type"]
    )

    return state


# -----------------------------------
# Node 4
# -----------------------------------

def escalation_node(state):

    state["escalation_summary"] = (
        generate_escalation_summary(
            state["session_summary"],
            state["memory_context"]
        )
    )

    return state


# -----------------------------------
# Conditional Routing
# -----------------------------------

def should_escalate(state):

    severity = (
        state["decision"]
        .get(
            "severity",
            "LOW"
        )
        .upper()
    )

    if severity == "CRITICAL":

        return "escalate"

    return END


# -----------------------------------
# Graph
# -----------------------------------

graph = StateGraph(
    SignalState
)

graph.add_node(
    "detect",
    signal_detector_node
)

graph.add_node(
    "assess",
    assessment_node
)

graph.add_node(
    "decide",
    decision_node
)

graph.add_node(
    "escalate",
    escalation_node
)

graph.set_entry_point(
    "detect"
)

graph.add_edge(
    "detect",
    "assess"
)

graph.add_edge(
    "assess",
    "decide"
)

graph.add_conditional_edges(
    "decide",
    should_escalate,
    {
        "escalate": "escalate",
        END: END
    }
)

graph.add_edge(
    "escalate",
    END
)

signal_graph = graph.compile()


# -----------------------------------
# Main Workflow
# -----------------------------------

def run_signal_workflow(
    student_id,
    session_summary,
    memory_context=""
):

    result = signal_graph.invoke(
        {
            "student_id": student_id,
            "session_summary": session_summary,
            "memory_context": memory_context,
            "signal_type": "",
            "assessment": {},
            "decision": {},
            "escalation_summary": ""
        }
    )

    signal_type = result.get(
        "signal_type",
        "UNKNOWN"
    )

    decision_data = result.get(
        "decision",
        {}
    )

    severity = decision_data.get(
        "severity",
        "LOW"
    )

    urgency = decision_data.get(
        "urgency",
        "TOMORROW"
    )

    manager_notify = decision_data.get(
        "manager_notify",
        "NO"
    )

    escalation_summary = result.get(
        "escalation_summary",
        ""
    )

    # --------------------------------
    # Action Status
    # --------------------------------

    if severity == "CRITICAL":

        actioned = "Manager Notified"

    elif severity == "HIGH":

        actioned = "Coach Review Required"

    else:

        actioned = "Pending"

    # --------------------------------
    # Save Signal
    # --------------------------------

    save_signal(
        student_id=student_id,
        signal_type=signal_type,
        severity=severity,
        urgency=urgency,
        reason=session_summary
    )

    # --------------------------------
    # Manager Alert
    # --------------------------------

    if (
        severity == "CRITICAL"
        and manager_notify == "YES"
    ):

        print("\n======================")
        print("🚨 MANAGER ALERT")
        print("======================")
        print(escalation_summary)

    return {
        "student_id": student_id,
        "signal_type": signal_type,
        "severity": severity,
        "urgency": urgency,
        "manager_notify": manager_notify,
        "actioned": actioned,
        "escalation_summary": escalation_summary
    }