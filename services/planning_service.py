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

        actioned = str(
            row.get(
                "actioned",
                ""
            )
        ).strip()

        signal_type = str(
            row.get(
                "signal_type",
                ""
            )
        ).strip().upper()

        severity = str(
            row.get(
                "severity",
                ""
            )
        ).strip().upper()

        if (
            actioned != "Done"
            and signal_type != ""
            and signal_type != "NONE"
        ):

            row["_priority"] = (
                SEVERITY_ORDER.get(
                    severity,
                    0
                )
            )

            pending.append(row)

    pending = sorted(
        pending,
        key=lambda x: x["_priority"],
        reverse=True
    )

    # print("\n===== PENDING SIGNALS =====")

    # for p in pending:
    #     print(
    #         p["student_id"],
    #         p["severity"],
    #         p["urgency"]
    #     )

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