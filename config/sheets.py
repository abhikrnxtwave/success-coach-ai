import os
import gspread

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

creds = Credentials.from_service_account_file(
    os.getenv("GOOGLE_CREDENTIALS_FILE"),
    scopes=SCOPES
)

client = gspread.authorize(creds)

spreadsheet = client.open_by_key(
    os.getenv("GOOGLE_SHEET_ID")
)