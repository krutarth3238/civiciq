import os
import pickle
import datetime
from typing import Dict, Any

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from services.cache import get_cached, set_cached

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
TOKEN_FILE = "token_sheets.pickle"
CREDENTIALS_FILE = "credentials.json"
SHEET_ID_FILE = "sheet_id.txt"
SHEET_TITLE = "CivicIQ Learning Tracker"
TAB_NAME = "Quiz Results"


def get_sheets_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("sheets", "v4", credentials=creds)


def get_or_create_sheet() -> str:
    """Get existing sheet ID or create a new CivicIQ tracker sheet."""
    if os.path.exists(SHEET_ID_FILE):
        with open(SHEET_ID_FILE, "r", encoding="utf-8") as f:
            sheet_id = f.read().strip()
            if sheet_id:
                return sheet_id

    service = get_sheets_service()
    spreadsheet = service.spreadsheets().create(
        body={
            "properties": {"title": SHEET_TITLE},
            "sheets": [{"properties": {"title": TAB_NAME}}],
        }
    ).execute()

    sheet_id = spreadsheet["spreadsheetId"]

    with open(SHEET_ID_FILE, "w", encoding="utf-8") as f:
        f.write(sheet_id)

    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range=f"{TAB_NAME}!A1",
        valueInputOption="RAW",
        body={
            "values": [[
                "Timestamp",
                "Topic",
                "Score",
                "Total Questions",
                "Difficulty"
            ]]
        },
    ).execute()

    return sheet_id


def log_quiz_result(topic: str, score: int, total: int, difficulty: str) -> Dict[str, Any]:
    """Logs a completed quiz result to Google Sheets."""
    try:
        service = get_sheets_service()
        sheet_id = get_or_create_sheet()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=f"{TAB_NAME}!A1",
            valueInputOption="RAW",
            body={"values": [[timestamp, topic, score, total, difficulty]]},
        ).execute()

        return {
            "status": "success",
            "message": f"Quiz result logged: {score}/{total} on {topic}",
        }
    except Exception as e:
        return {"error": str(e), "service": "Google Sheets"}


def get_learning_progress() -> Dict[str, Any]:
    """Fetches all quiz history from Google Sheets."""
    cache_key = "learning_progress"
    cached = get_cached(cache_key)
    if cached:
        return cached

    try:
        service = get_sheets_service()
        sheet_id = get_or_create_sheet()
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range=f"{TAB_NAME}!A1:E100",
        ).execute()

        rows = result.get("values", [])
        payload = {"progress": rows}
        set_cached(cache_key, payload)
        return payload
    except Exception as e:
        return {"error": str(e), "service": "Google Sheets"}