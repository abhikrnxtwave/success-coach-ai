from datetime import (
    datetime,
    timedelta
)

from config.sheets import (
    spreadsheet
)


SEVERITY_ORDER = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1
}


def get_pending_signals():

    sheet = spreadsheet.worksheet(
        "signal_sheet"
    )

    rows = sheet.get_all_records()

    pending = []

    for row in rows:

        urgency = str(
            row.get(
                "urgency",
                ""
            )
        ).upper()

        actioned = str(
            row.get(
                "actioned",
                ""
            )
        )

        signal_type = str(
            row.get(
                "signal_type",
                ""
            )
        ).upper()

        severity = str(
            row.get(
                "severity",
                ""
            )
        ).upper()

        # Only signals that need coach attention TODAY
        if (
            urgency == "TODAY"
            and actioned != "Done"
            and signal_type != "NONE"
        ):

            row["_priority"] = (
                SEVERITY_ORDER.get(
                    severity,
                    0
                )
            )

            pending.append(
                row
            )

    pending = sorted(
        pending,
        key=lambda x: x["_priority"],
        reverse=True
    )

    return pending


def assign_time_slots(
    planned_sessions
):

    current_time = datetime.strptime(
        "09:00",
        "%H:%M"
    )

    for session in planned_sessions:

        session["time"] = (
            current_time.strftime(
                "%I:%M %p"
            )
        )

        duration = int(
            session.get(
                "duration",
                30
            )
        )

        current_time += timedelta(
            minutes=duration + 15
        )

    return planned_sessions