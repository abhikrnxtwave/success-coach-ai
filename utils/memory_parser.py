def split_memory(
    memory_text
):

    facts = ""
    summary = ""

    if "SUMMARY:" in memory_text:

        parts = memory_text.split(
            "SUMMARY:"
        )

        facts = (
            parts[0]
            .replace(
                "FACTS:",
                ""
            )
            .strip()
        )

        summary = (
            parts[1]
            .strip()
        )

    return facts, summary