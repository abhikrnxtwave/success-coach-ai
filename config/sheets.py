import os
import gspread
import streamlit as st

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

if os.path.exists("credentials.json"):
    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )
else:
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

client = gspread.authorize(creds)

spreadsheet = client.open_by_key(
    os.getenv("GOOGLE_SHEET_ID") or st.secrets["GOOGLE_SHEET_ID"]
)