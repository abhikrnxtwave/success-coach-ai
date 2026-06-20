import json

from config.llm import (
    get_ai_response
)


def detect_signal(
    session_summary
):

    prompt = f"""
You are a student coach.

Analyze the session.

Detect the primary concern.

Possible values:

ACADEMIC_RISK
STRESS
ATTENDANCE
MOTIVATION
NONE

Return ONLY one value.

Session:

{session_summary}
"""

    response = get_ai_response(
        [
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.strip()


def assess_signal(
    session_summary,
    memory_context,
    signal_type
):

    prompt = f"""
You are a Student Success Analyst.

CURRENT SIGNAL:
{signal_type}

CURRENT SESSION:
{session_summary}

PAST MEMORY:
{memory_context}

Determine severity.

Rules:

LOW
- Normal conversation
- No meaningful risk

MEDIUM
- Academic struggles
- Exam anxiety
- Attendance concerns

HIGH
- Exam within 48 hours and unprepared
- Wants to drop course
- Severe stress impacting studies
- Repeated poor performance

CRITICAL
- Self harm thoughts
- Hopelessness
- Panic attacks
- Serious mental health concern
- Repeated distress pattern

Return ONLY JSON:

{{
    "severity":"LOW|MEDIUM|HIGH|CRITICAL",
    "reason":"short explanation"
}}
"""

    response = get_ai_response(
        [
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    try:

        return json.loads(
            response
        )

    except:

        return {
            "severity": "LOW",
            "reason": "Could not parse severity"
        }


def decide_action(
    session_summary,
    memory_context,
    signal_type
):

    prompt = f"""
You are a Student Success Risk Assessment Agent.

CURRENT SESSION:
{session_summary}

PAST MEMORY:
{memory_context}

SIGNAL TYPE:
{signal_type}

Determine:

1. Severity
2. Urgency
3. Manager Notification

Severity Rules:

LOW
- Normal conversation

MEDIUM
- Academic struggle
- Exam anxiety

HIGH
- Exam within 48 hours and unprepared
- Wants to drop course
- Severe stress

CRITICAL
- Self harm
- Hopelessness
- Panic attacks
- Serious emotional crisis

Urgency Rules:

TODAY
- HIGH
- CRITICAL
- Exam within 48 hours

TOMORROW
- LOW
- MEDIUM

Manager Notification:

YES
- CRITICAL only

NO
- Otherwise

Return ONLY JSON:

{{
    "severity":"LOW|MEDIUM|HIGH|CRITICAL",
    "urgency":"TODAY|TOMORROW",
    "manager_notify":"YES|NO",
    "reason":"short explanation"
}}
"""

    response = get_ai_response(
        [
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    try:

        return json.loads(
            response
        )

    except:

        return {
            "severity": "LOW",
            "urgency": "TOMORROW",
            "manager_notify": "NO",
            "reason": "Could not parse response"
        }