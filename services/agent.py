from langchain_core.tools import tool

from config.llm import llm

from tools.student_tool import (
    get_student_context,
    get_student_identity
)
from tools.knowledge_tool import (
    get_knowledge_context
)
from tools.memory_tool import (
    search_memory
)


ROUTER_SYSTEM_PROMPT = """You are the routing layer for a Student Success AI coach.

Look at the user's message and call whichever tools are needed to
gather context for answering it. You may call more than one tool
if the question genuinely needs more than one kind of context.
Call no tools for general questions unrelated to the student,
their coursework, or past sessions.

Do not answer the user. Only decide which tools to call."""


def build_tools(query, student_name):
    """
    Wraps each context source as a zero-argument LangChain tool.

    student_name and query are captured via closure rather than
    exposed as tool arguments, since they're already known values —
    the model's only job is picking the right tool(s), not inventing
    arguments for them.

    Memory is deliberately NOT one of these tools — see run_agent().
    """

    @tool
    def get_identity_info() -> str:
        """Use for greetings, introductions, casual small talk,
        or when the user asks who the currently selected student is.
        Do not use this for performance, scores, or attendance questions."""
        return get_student_identity(student_name)

    @tool
    def get_performance_data() -> str:
        """Use when the user asks about the student's attendance,
        exam scores, grades, performance trends, or upcoming exams."""
        return get_student_context(student_name)

    @tool
    def search_knowledge_base() -> str:
        """Use for study-related questions: subject concepts,
        syllabus content, definitions, or how a topic works."""
        return get_knowledge_context(query)

    return [
        get_identity_info,
        get_performance_data,
        search_knowledge_base,
    ]


# Maps each tool name to the context bucket it fills in
# run_agent's return value. Add an entry here whenever you add a tool.
TOOL_TO_CONTEXT_KEY = {
    "get_identity_info": "student_context",
    "get_performance_data": "student_context",
    "search_knowledge_base": "knowledge_context",
}


def run_agent(query, student_name):

    memory_context = ""

    try:
        memory_context = search_memory(query, student_name)
    except Exception as e:
        print(f"Memory Tool Error: {e}")

    tools = build_tools(query, student_name)
    tool_lookup = {t.name: t for t in tools}

    llm_with_tools = llm.bind_tools(tools)

    try:
        routing_decision = llm_with_tools.invoke([
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ])
        tool_calls = routing_decision.tool_calls or []
    except Exception as e:
        print(f"Agent Routing Error: {e}")
        tool_calls = []

    context = {
        "student_context": "",
        "knowledge_context": "",
    }

    called_tools = []

    for call in tool_calls:

        tool_name = call["name"]
        matched_tool = tool_lookup.get(tool_name)

        if not matched_tool:
            continue

        try:
            result = matched_tool.invoke(call.get("args", {}))
        except Exception as e:
            print(f"Tool Execution Error ({tool_name}): {e}")
            continue

        context_key = TOOL_TO_CONTEXT_KEY[tool_name]

        if context[context_key]:
            context[context_key] += "\n\n" + result
        else:
            context[context_key] = result

        called_tools.append(tool_name)

    return {
        "decision": called_tools or ["none"],
        "student_context": context["student_context"],
        "knowledge_context": context["knowledge_context"],
        "memory_context": memory_context,
    }