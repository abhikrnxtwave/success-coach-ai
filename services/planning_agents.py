from config.llm import get_ai_response


def recommend_session_type(
    signal_type,
    severity,
    reason
):

    prompt = f"""
You are a Student Success Coach.

Signal Type:
{signal_type}

Severity:
{severity}

Reason:
{reason}

Choose ONE:

ACADEMIC_RESCUE
STRESS_COACHING
ATTENDANCE_INTERVENTION
MOTIVATION_SESSION
PROGRESS_REVIEW

Return ONLY the value.
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


def estimate_duration(
    severity
):

    severity = severity.upper()

    if "CRITICAL" in severity:
        return 45

    if "HIGH" in severity:
        return 30

    if "MEDIUM" in severity:
        return 20

    return 15