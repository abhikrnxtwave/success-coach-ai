from config.sheets import spreadsheet


def get_all_students():

    roster_sheet = spreadsheet.worksheet(
        "roster"
    )

    rows = roster_sheet.get_all_records()

    return [
        row["name"]
        for row in rows
    ]


def get_student_profile(student_name):

    roster_sheet = spreadsheet.worksheet(
        "roster"
    )

    scores_sheet = spreadsheet.worksheet(
        "exam_scores"
    )

    attendance_sheet = spreadsheet.worksheet(
        "attendance"
    )

    exams_sheet = spreadsheet.worksheet(
        "exam_schedule"
    )

    roster_rows = roster_sheet.get_all_records()

    student = next(
        (
            row
            for row in roster_rows
            if row["name"] == student_name
        ),
        None
    )

    if not student:
        return None

    student_id = student["student_id"]

    scores = [
        row
        for row in scores_sheet.get_all_records()
        if row["student_id"] == student_id
    ]

    attendance = [
        row
        for row in attendance_sheet.get_all_records()
        if row["student_id"] == student_id
    ]

    exams = [
        row
        for row in exams_sheet.get_all_records()
        if row["student_id"] == student_id
    ]

    return {
        "student": student,
        "scores": scores,
        "attendance": attendance,
        "exams": exams
    }