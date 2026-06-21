from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    END
)

from tools.memory_tool import (
    search_memory
)

from services.signal_reader import (
    get_signals
)

from services.brief_agent import (
    generate_brief
)


class BriefState(TypedDict):

    student_id: str

    memory_context: str

    signal_history: list

    brief: dict


# --------------------------------
# Node 1
# Load Memory
# --------------------------------

def load_memory_node(state):

    student_id = state[
        "student_id"
    ]

    memory_context = search_memory(
        f"Student: {student_id}",
        student_id
    )

    state[
        "memory_context"
    ] = memory_context

    return state


# --------------------------------
# Node 2
# Load Signal History
# --------------------------------

def load_signal_history_node(state):

    student_id = state[
        "student_id"
    ]

    all_signals = get_signals()

    history = []

    for signal in all_signals:

        if (
            str(
                signal.get(
                    "student_id",
                    ""
                )
            ).strip()
            ==
            student_id.strip()
        ):

            history.append(
                signal
            )

    history = sorted(
        history,
        key=lambda x:
        x.get(
            "timestamp",
            ""
        ),
        reverse=True
    )

    state[
        "signal_history"
    ] = history

    return state


# --------------------------------
# Node 3
# Generate Brief
# --------------------------------

def generate_brief_node(state):

    brief = generate_brief(

        student_id=
        state[
            "student_id"
        ],

        memory_context=
        state[
            "memory_context"
        ],

        signal_history=
        state[
            "signal_history"
        ]
    )

    state[
        "brief"
    ] = brief

    return state


# --------------------------------
# Graph
# --------------------------------

graph = StateGraph(
    BriefState
)

graph.add_node(
    "load_memory",
    load_memory_node
)

graph.add_node(
    "load_signal_history",
    load_signal_history_node
)

graph.add_node(
    "generate_brief",
    generate_brief_node
)

graph.set_entry_point(
    "load_memory"
)

graph.add_edge(
    "load_memory",
    "load_signal_history"
)

graph.add_edge(
    "load_signal_history",
    "generate_brief"
)

graph.add_edge(
    "generate_brief",
    END
)

brief_graph = graph.compile()


# --------------------------------
# Workflow
# --------------------------------

def run_brief_workflow(
    student_id
):

    result = brief_graph.invoke(
        {
            "student_id":
            student_id,

            "memory_context":
            "",

            "signal_history":
            [],

            "brief":
            {}
        }
    )

    return result[
        "brief"
    ]