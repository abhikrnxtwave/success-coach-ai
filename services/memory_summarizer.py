from config.llm import get_ai_response


def generate_memory_objects(
    conversation_text
):

    prompt = f"""
You are a student success coach.

Analyze the conversation.

Extract:

FACTS:
- Long-term student information
- Learning preferences
- Recurring challenges
- Goals
- Stress triggers

SUMMARY:
- What was discussed
- What decisions were made
- What recommendations were given

Return EXACTLY in this format:

FACTS:
...

SUMMARY:
...

Conversation:

{conversation_text}
"""

    response = get_ai_response(
        [
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response