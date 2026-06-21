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

    plan_summary: list

    critical_conflicts: list

# --------------------------------
# Node 1
# --------------------------------

def load_signals_node(state):

    signals = get_pending_signals()

    state["signals"] = signals

    return state


# --------------------------------
# Node 2
# --------------------------------

def planning_node(state):

    signals = state["signals"]

    planned = []

    deferred = []

    plan_summary = []

    critical_conflicts = []

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

    SERIOUS_LEVELS = [
        "CRITICAL"
    ]

    # --------------------------------
    # Step 3: Detect critical conflict
    # BEFORE any scheduling happens.
    #
    # If two or more CRITICAL students
    # are competing for capacity that
    # can't fit all of them, the AI
    # must NOT auto-pick who gets the
    # slot. Pull them out of the
    # scheduling pool entirely and let
    # the coach decide.
    # --------------------------------

    critical_today = [
        s for s in signals
        if str(s.get("severity", "")).upper() == "CRITICAL"
    ]

    if len(critical_today) > 1:

        critical_minutes_needed = sum(
            estimate_duration(s["severity"])
            for s in critical_today
        )

        if remaining_minutes < critical_minutes_needed:

            critical_conflicts = critical_today

            plan_summary.append(
                {
                    "type": "COACH_DECISION_REQUIRED",
                    "reason":
                    "Multiple critical students require attention but capacity is limited.",
                    "message": (
                        f"{len(critical_today)} critical students need coaching today, "
                        f"but only {remaining_minutes} minutes remain. "
                        "Coach decision required — select who is scheduled today."
                    )
                }
            )

            conflict_ids = {
                s["student_id"] for s in critical_today
            }

            signals = [
                s for s in signals
                if s["student_id"] not in conflict_ids
            ]

    for signal in signals:

        severity = str(
            signal.get(
                "severity",
                ""
            )
        ).upper()

        urgency = str(
            signal.get(
                "urgency",
                ""
            )
        ).upper()

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

        # --------------------------------
        # HIGH / MEDIUM / LOW TOMORROW
        # --------------------------------

        if (
            severity != "CRITICAL"
            and urgency == "TOMORROW"
        ):

            deferred.append(
                {
                    "student_id": signal["student_id"],
                    "reason": "Recommended for tomorrow"
                }
            )

            plan_summary.append(
                {
                    "type": "DEFERRED",
                    "student_id": signal["student_id"],
                    "reason": "Urgency is TOMORROW",
                    "message": (
                        f"{signal['student_id']} scheduled for tomorrow "
                        "(recommended urgency)."
                    )
                }
            )

            continue

        # --------------------------------
        # Schedule Today
        # --------------------------------

        if duration <= remaining_minutes:

            planned.append(session)

            remaining_minutes -= duration

            if severity == "CRITICAL":

                plan_summary.append(
                    {
                        "type": "NEW_SERIOUS_CONCERN",
                        "student_id": signal["student_id"],
                        "reason": signal["reason"],
                        "message": (
                            f"{signal['student_id']} added to today's schedule "
                            f"because of a critical signal: {signal['reason']}"
                        )
                    }
                )

        else:

            if severity == "CRITICAL":

                # A single critical signal still didn't fit (e.g. it alone
                # exceeds remaining capacity). Never silently defer a
                # critical signal like a routine one — surface it.

                critical_conflicts.append(
                    {
                        "student_id": signal["student_id"],
                        "signal_type": signal["signal_type"],
                        "severity": severity,
                        "reason": signal["reason"]
                    }
                )

                plan_summary.append(
                    {
                        "type": "COACH_DECISION_REQUIRED",
                        "student_id": signal["student_id"],
                        "reason": "Critical student arrived but no capacity remains.",
                        "message": (
                            f"{signal['student_id']} is CRITICAL but today's "
                            "capacity is full. Coach decision required."
                        )
                    }
                )

            else:

                deferred.append(
                    {
                        "student_id": signal["student_id"],
                        "reason": "Coach capacity reached today"
                    }
                )

                plan_summary.append(
                    {
                        "type": "MOVED_TO_TOMORROW",
                        "student_id": signal["student_id"],
                        "reason": "Coach capacity reached",
                        "message": (
                            f"{signal['student_id']} moved to tomorrow because "
                            "today's coaching capacity is full."
                        )
                    }
                )

    # Assign calendar times
    planned = assign_time_slots(
        planned
    )

    state["planned_sessions"] = planned

    state["deferred_students"] = deferred

    state["plan_summary"] = plan_summary

    state["critical_conflicts"] = critical_conflicts

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

def run_planning_workflow(previous_sessions=None):
    """
    previous_sessions: the planned_sessions list from the LAST plan that
    was shown on the dashboard (optional). When provided, this lets us
    detect that a student who was already scheduled got moved to a new
    time slot because of a newly-arrived signal, and surface that in the
    plan summary (e.g. "Rahul rescheduled from 10:00 AM to 11:00 AM.").
    """

    result = planning_graph.invoke(
        {
            "signals": [],
            "planned_sessions": [],
            "deferred_students": [],
            "calendar_events": [],
            "plan_summary": [],
            "critical_conflicts": []
        }
    )

    plan_summary = result["plan_summary"]

    if previous_sessions:

        previous_times = {
            session["student_id"]: session.get("time")
            for session in previous_sessions
        }

        for session in result["planned_sessions"]:

            old_time = previous_times.get(session["student_id"])

            new_time = session.get("time")

            if old_time and new_time and old_time != new_time:

                plan_summary.append(
                    {
                        "type": "RESCHEDULED",
                        "student_id": session["student_id"],
                        "reason": "Time slot changed due to a new higher-priority signal.",
                        "message": (
                            f"{session['student_id']} rescheduled from "
                            f"{old_time} to {new_time}."
                        )
                    }
                )

    return {
        "planned_sessions":
        result["planned_sessions"],

        "deferred_students":
        result["deferred_students"],

        "calendar_events":
        result["calendar_events"],

        "plan_summary":
        plan_summary,

        "critical_conflicts":
        result["critical_conflicts"]
    }


# --------------------------------
# Manual Coach Decision
# (Scenario 3 — biggest M9 feature)
# --------------------------------

def resolve_critical_conflict(selected_student, other_students):
    """
    Called when the coach manually picks which CRITICAL student gets
    today's remaining slot, out of a group of conflicting critical
    signals the AI refused to auto-decide between.

    selected_student: the signal dict the coach chose to schedule today.
    other_students: the remaining conflicting signal dicts — these get
                     moved to tomorrow since the slot is now taken.

    Returns (scheduled_session, calendar_event, deferred_list, summary_item)
    so the caller (the dashboard) can merge them into the existing plan.
    """

    session_type = recommend_session_type(
        selected_student["signal_type"],
        selected_student["severity"],
        selected_student["reason"]
    )

    duration = estimate_duration(
        selected_student["severity"]
    )

    session = {
        "student_id": selected_student["student_id"],
        "signal_type": selected_student["signal_type"],
        "severity": selected_student["severity"],
        "session_type": session_type,
        "duration": duration,
        "reason": selected_student["reason"]
    }

    scheduled = assign_time_slots([session])

    scheduled_session = scheduled[0]

    event = create_calendar_event(
        student_id=scheduled_session["student_id"],
        session_type=scheduled_session["session_type"],
        start_time=scheduled_session["time"],
        duration=scheduled_session["duration"]
    )

    deferred = []

    for student in other_students:

        deferred.append(
            {
                "student_id": student["student_id"],
                "reason":
                "Coach selected another critical student for today's remaining slot."
            }
        )

    summary_item = {
        "type": "COACH_DECISION_MADE",
        "student_id": scheduled_session["student_id"],
        "reason": "Coach manually resolved a critical capacity conflict.",
        "message": (
            f"Coach scheduled {scheduled_session['student_id']} for today. "
            f"{len(deferred)} other critical student(s) moved to tomorrow."
        )
    }

    return scheduled_session, event, deferred, summary_item