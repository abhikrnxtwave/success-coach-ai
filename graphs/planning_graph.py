from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    END
)

from services.planning_service import (
    get_pending_signals,
    assign_time_slots
)

from services.planning_agents import (
    recommend_session_type,
    estimate_duration
)


from services.calendar_service import (
    create_calendar_event
)


class PlanningState(TypedDict):

    signals: list

    planned_sessions: list

    deferred_students: list

    calendar_events: list

# --------------------------------
# Node 1
# --------------------------------

def load_signals_node(state):

    state["signals"] = (
        get_pending_signals()
    )

    return state


# --------------------------------
# Node 2
# --------------------------------

def planning_node(state):

    signals = state["signals"]

    planned = []

    deferred = []

    # Coach capacity
    remaining_minutes = 240

    priority_order = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1
    }

    signals.sort(
        key=lambda x:
        priority_order.get(
            str(
                x.get(
                    "severity",
                    ""
                )
            ).upper(),
            0
        ),
        reverse=True
    )

    for signal in signals:

        session_type = (
            recommend_session_type(
                signal["signal_type"],
                signal["severity"],
                signal["reason"]
            )
        )

        duration = (
            estimate_duration(
                signal["severity"]
            )
        )

        session = {

            "student_id":
            signal["student_id"],

            "signal_type":
            signal["signal_type"],

            "severity":
            signal["severity"],

            "session_type":
            session_type,

            "duration":
            duration,

            "reason":
            signal["reason"]
        }

        if duration <= remaining_minutes:

            planned.append(
                session
            )

            remaining_minutes -= duration

        else:

            deferred.append(
                {
                    "student_id":
                    signal["student_id"],

                    "reason":
                    "Coach capacity reached today"
                }
            )

    # Assign calendar times
    planned = assign_time_slots(
        planned
    )

    state[
        "planned_sessions"
    ] = planned

    state[
        "deferred_students"
    ] = deferred

    return state




# --------------------------------
# Node 3
# --------------------------------

def calendar_node(state):

    events = []

    for session in state["planned_sessions"]:

        event = create_calendar_event(
            student_id=session["student_id"],
            session_type=session["session_type"],
            start_time=session["time"],
            duration=session["duration"]
        )

        events.append(
            event
        )

    state[
        "calendar_events"
    ] = events

    return state

# --------------------------------
# Graph
# --------------------------------

graph = StateGraph(
    PlanningState
)

graph.add_node(
    "load_signals",
    load_signals_node
)

graph.add_node(
    "plan",
    planning_node
)

graph.add_node(
    "calendar",
    calendar_node
)

graph.set_entry_point(
    "load_signals"
)

graph.add_edge(
    "load_signals",
    "plan"
)

graph.add_edge(
    "plan",
    "calendar"
)

graph.add_edge(
    "calendar",
    END
)

planning_graph = graph.compile()


# --------------------------------
# Workflow
# --------------------------------

def run_planning_workflow():

    result = planning_graph.invoke(
        {
            "signals": [],
            "planned_sessions": [],
            "deferred_students": [],
            "calendar_events": []
        }
    )

    return {
        "planned_sessions":
        result["planned_sessions"],

        "deferred_students":
        result["deferred_students"],

        "calendar_events":
        result["calendar_events"]
    }