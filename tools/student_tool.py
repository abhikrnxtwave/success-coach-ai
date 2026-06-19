from services.student_service import (
    get_student_profile
)


def get_student_identity(
    student_name
):
    """
    Lightweight context for greetings
    and personal conversations.
    """

    student_profile = get_student_profile(
        student_name
    )

    return f"""
Selected Student

Name:
{student_profile['student']['name']}

This is the currently selected student.

For greetings and casual conversation:
- Use the student's name naturally.
- Do not mention program, cohort, scores,
  attendance or exams unless asked.
"""
    

def get_student_context(
    student_name
):

    student_profile = get_student_profile(
        student_name
    )

    attendance_records = (
        student_profile["attendance"]
    )

    total_classes_scheduled = sum(
        int(row["classes_scheduled"] or 0)
        for row in attendance_records
    )

    total_classes_attended = sum(
        int(row["classes_attended"] or 0)
        for row in attendance_records
    )

    avg_attendance_pct = 0

    if total_classes_scheduled > 0:

        avg_attendance_pct = round(
            (
                total_classes_attended
                / total_classes_scheduled
            ) * 100,
            2
        )

    scores_text = ""

    for score in student_profile["scores"]:

        scores_text += (
            f"{score['subject']}: "
            f"{score['score']}/{score['max_score']}\n"
        )

    exam_text = ""

    for exam in student_profile["exams"]:

        exam_text += (
            f"{exam['subject']} | "
            f"{exam['exam_type']} | "
            f"{exam['exam_date']}\n"
        )

    return f"""
Student Information

Name:
{student_profile['student']['name']}

Program:
{student_profile['student']['program']}

Cohort:
{student_profile['student']['cohort']}

Attendance Summary

Average Attendance:
{avg_attendance_pct}%

Classes Attended:
{total_classes_attended}

Classes Scheduled:
{total_classes_scheduled}

Exam Scores:
{scores_text}

Upcoming Exams:
{exam_text}

When discussing this student:

- Use actual attendance data.
- Use actual exam scores.
- Use upcoming exam dates.
- Mention areas needing attention.
- Mention attendance concerns if attendance is low.
- Mention upcoming exams when relevant.
"""