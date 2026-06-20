from datetime import datetime

from config.sheets import (
    spreadsheet
)


def save_signal(
    student_id,
    signal_type,
    severity,
    urgency,
    reason
):

    sheet = spreadsheet.worksheet(
        "signal_sheet"
    )

    severity_upper = severity.upper()

    if "CRITICAL" in severity_upper:

        actioned = (
            "Manager Notified"
        )

    elif "HIGH" in severity_upper:

        actioned = (
            "Coach Review Required"
        )

    else:

        actioned = (
            "Pending"
        )

    sheet.append_row(
        [
            student_id,
            signal_type,
            severity,
            urgency,
            reason,
            datetime.now().isoformat(),
            actioned
        ]
    )