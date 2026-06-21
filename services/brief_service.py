from config.sheets import spreadsheet


def get_student_history(
    student_id
):

    sheet = spreadsheet.worksheet(
        "signal_sheet"
    )

    rows = sheet.get_all_records()

    history = []

    for row in rows:

        if row["student_id"] == student_id:

            history.append(
                row
            )

    history = sorted(
        history,
        key=lambda x: x["timestamp"],
        reverse=True
    )

    return history