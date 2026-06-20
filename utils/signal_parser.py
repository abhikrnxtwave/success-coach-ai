def parse_signal_result(
    graph_output
):

    assessment = (
        graph_output["assessment"]
    )

    decision = (
        graph_output["decision"]
    )

    severity = "LOW"
    urgency = "TOMORROW"
    reason = ""

    for line in assessment.split("\n"):

        if line.startswith(
            "SEVERITY:"
        ):

            severity = (
                line.replace(
                    "SEVERITY:",
                    ""
                ).strip()
            )

        if line.startswith(
            "REASON:"
        ):

            reason = (
                line.replace(
                    "REASON:",
                    ""
                ).strip()
            )

    for line in decision.split("\n"):

        if line.startswith(
            "URGENCY:"
        ):

            urgency = (
                line.replace(
                    "URGENCY:",
                    ""
                ).strip()
            )

    return {
        "severity": severity,
        "urgency": urgency,
        "reason": reason
    }