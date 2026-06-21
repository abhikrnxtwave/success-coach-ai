import os
from datetime import datetime, timedelta

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

try:
    import streamlit as st
except ImportError:
    st = None


CALENDAR_ID = os.getenv("CALENDAR_ID")

SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]


def get_credentials():

    # Streamlit Cloud
    if st:
        try:
            return Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=SCOPES
            )
        except Exception:
            pass

    # Local
    return Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )


creds = get_credentials()

calendar_service = build(
    "calendar",
    "v3",
    credentials=creds
)


def create_calendar_event(
    student_id,
    session_type,
    start_time,
    duration
):

    # Example:
    # start_time = "09:00 AM"

    today = datetime.now().date()

    start_dt = datetime.strptime(
        start_time,
        "%I:%M %p"
    )

    start_dt = datetime.combine(
        today,
        start_dt.time()
    )

    end_dt = start_dt + timedelta(
        minutes=duration
    )

    event = {
        "summary":
            f"Coaching Session - {student_id}",

        "description":
            f"Session Type: {session_type}",

        "start": {
            "dateTime":
                start_dt.isoformat(),

            "timeZone":
                "Asia/Kolkata"
        },

        "end": {
            "dateTime":
                end_dt.isoformat(),

            "timeZone":
                "Asia/Kolkata"
        }
    }

    result = (
        calendar_service.events()
        .insert(
            calendarId=CALENDAR_ID,
            body=event
        )
        .execute()
    )

    return {
        "event_id":
            result["id"],

        "event_link":
            result["htmlLink"],

        "title":
            event["summary"],

        "start_time":
            start_time,

        "duration":
            duration
    }