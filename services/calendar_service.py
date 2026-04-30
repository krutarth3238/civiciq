import os
import pickle
import datetime
from typing import Dict, Any

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_FILE = "token_calendar.pickle"
CREDENTIALS_FILE = "credentials.json"


def get_calendar_service():
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

    return build("calendar", "v3", credentials=creds)


def add_election_reminder(title: str, date: str, description: str) -> Dict[str, Any]:
    """Adds an election-related civic date to Google Calendar (date format: YYYY-MM-DD)."""
    try:
        service = get_calendar_service()

        start_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        end_date = start_date + datetime.timedelta(days=1)

        event = {
            "summary": f"📅 {title}",
            "description": description,
            "start": {"date": start_date.isoformat()},
            "end": {"date": end_date.isoformat()},
            "reminders": {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": 1440}],
            },
        }

        service.events().insert(calendarId="primary", body=event).execute()

        return {
            "status": "success",
            "message": f"Added '{title}' to your calendar on {date}",
        }
    except Exception as e:
        return {"error": str(e), "service": "Google Calendar"}


def get_upcoming_civic_events() -> Dict[str, Any]:
    """Fetches upcoming election/civic events from Google Calendar."""
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + "Z"

        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=5,
            singleEvents=True,
            orderBy="startTime",
            q="election",
        ).execute()

        events = events_result.get("items", [])

        if not events:
            return {"events": [], "message": "No upcoming civic events found"}

        return {
            "events": [
                {
                    "title": e.get("summary", "Untitled event"),
                    "date": e["start"].get("date", e["start"].get("dateTime", "")),
                }
                for e in events
            ]
        }
    except Exception as e:
        return {"error": str(e), "service": "Google Calendar"}