from config.llm import (
    get_ai_response
)


def generate_escalation_summary(
    session_summary,
    memory_context
):

    prompt = f"""
You are a senior student success manager.

Analyze the case.

Historical Memory:

{memory_context}

Current Session:

{session_summary}

Create:

1. Main Concern
2. Historical Pattern
3. Risk Assessment
4. Recommended Action

Keep concise.
"""

    return get_ai_response(
        [
            {
                "role": "user",
                "content": prompt
            }
        ]
    )