from config.llm import get_ai_response

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


def decide_tools(user_query):

    planner_prompt = f"""
You are an AI routing agent.

Available tools:

1. student_identity
   - greetings
   - introductions
   - personal conversation
   - who is the selected student

2. student_data
   - scores
   - attendance
   - exams
   - performance

3. knowledge_base
   - study topics
   - concepts
   - syllabus content

4. memory
   - previous discussions
   - student history
   - progress
   - habits
   - recurring struggles

Return ONLY one of:

student_identity
student_data
knowledge_base
both
none

Rules:

Use memory when:

- asking about previous sessions
- asking for progress
- asking what happened before
- asking about recurring challenges
- asking for coaching continuity

- Greetings, introductions, casual conversation,
  "who am I", "who is the selected student"
  -> student_identity

- Student performance, attendance, scores, exams
  -> student_data

- Study topics, concepts, syllabus content
  -> knowledge_base

- Questions needing both student information
  and study information
  -> both

- Completely unrelated general questions
  -> none

Return ONLY the routing value.

Do not explain.
Do not add punctuation.

Question:
{user_query}
"""

    try:
        response = get_ai_response(
            [
                {
                    "role": "user",
                    "content": planner_prompt
                }
            ]
        )

        decision = response.strip().lower()

        valid_decisions = [
            "student_identity",
            "student_data",
            "knowledge_base",
            "both",
            "none"
        ]

        for value in valid_decisions:

            if decision == value:
                return value

        for value in valid_decisions:

            if value in decision:
                return value

        return "none"

    except Exception as e:

        print(
            f"Agent Planner Error: {e}"
        )

        return "none"


def run_agent(
    query,
    student_name
):

    decision = decide_tools(
        query
    )

    student_context = ""
    knowledge_context = ""
    memory_context = ""

    #for memory
    memory_context = ""

    try:

        memory_context = search_memory(
            query,
            student_name
        )

    except Exception as e:

        print(
            f"Memory Tool Error: {e}"
        )

    # -------------------------
    # Student Identity Tool
    # -------------------------

    if decision == "student_identity":

        try:

            student_context = (
                get_student_identity(
                    student_name
                )
            )

        except Exception as e:

            print(
                f"Student Identity Tool Error: {e}"
            )

    # -------------------------
    # Student Data Tool
    # -------------------------

    elif decision in [
        "student_data",
        "both"
    ]:

        try:

            student_context = (
                get_student_context(
                    student_name
                )
            )

        except Exception as e:

            print(
                f"Student Tool Error: {e}"
            )

    # -------------------------
    # Knowledge Tool
    # -------------------------

    if decision in [
        "knowledge_base",
        "both"
    ]:

        try:

            knowledge_context = (
                get_knowledge_context(
                    query
                )
            )

        except Exception as e:

            print(
                f"Knowledge Tool Error: {e}"
            )

    return {
        "decision": decision,
        "student_context": student_context,
        "knowledge_context": knowledge_context,
        "memory_context": memory_context
    }