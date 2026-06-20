from config.sheets import get_sheet

def get_signals():

    sheet = get_sheet(
        "signal_sheet"
    )

    records = sheet.get_all_records()

    return records