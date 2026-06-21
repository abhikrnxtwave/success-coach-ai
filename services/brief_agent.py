import os
import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "gpt-5"
)


def generate_brief(
    student_id,
    memory_context,
    signal_history
):

    history_text = ""

    for signal in signal_history[:5]:

        history_text += f"""

Date: {signal.get('timestamp')}

Signal Type: {signal.get('signal_type')}

Severity: {signal.get('severity')}

Reason:
{signal.get('reason')}

"""

    prompt = f"""
You are preparing a Student Success Coach for an upcoming student session.

The coach has not recently reviewed the student's history.

Your job is to generate a concise coach preparation brief.

=================================
STUDENT
=================================

{student_id}

=================================
LONG TERM MEMORY
=================================

{memory_context}

This contains historical facts, preferences, goals, struggles, progress,
and previous coaching memories.

=================================
RECENT SESSION HISTORY
=================================

{history_text}

This contains previous conversations, coaching discussions,
recommendations, decisions, and support provided.

=================================
TASK
=================================

Create a coach briefing that helps the coach quickly understand:

1. Who the student is and what they are currently dealing with
2. What happened in recent conversations
3. Important topics already discussed
4. Recommendations or actions previously suggested
5. What should be followed up in today's meeting
6. Good coaching questions to continue the conversation

DO NOT repeat raw logs.

DO NOT copy conversation history.

Summarize like internal coaching notes.

Return ONLY valid JSON.

{{
    "student_snapshot": "",
    "last_conversation_summary": "",
    "what_was_discussed": "",
    "decisions_and_recommendations": "",
    "follow_up_topics": "",
    "conversation_starters": []
}}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You generate coaching briefs."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={
            "type": "json_object"
        }
    )

    content = (
        response.choices[0]
        .message
        .content
    )

    try:

        return json.loads(content)

    except Exception:

        return {
            "current_situation":
                "Unable to generate summary.",

            "changes_since_last_session":
                "No changes detected.",

            "open_concerns":
                "No concerns identified.",

            "conversation_starters": [
                "How have things been since our last conversation?"
            ]
        }