import os
import pickle
import base64
from typing import Dict, Any
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]
TOKEN_FILE = "token_gmail.pickle"
CREDENTIALS_FILE = "credentials.json"


def get_gmail_service():
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

    return build("gmail", "v1", credentials=creds)


def send_civic_summary(to_email: str, summary: str) -> Dict[str, Any]:
    """Sends a civic education learning summary via Gmail."""
    try:
        service = get_gmail_service()

        message = MIMEText(
            f"Your CivicIQ Learning Summary\n\n{summary}\n\n"
            f"Keep learning — an informed voter is a powerful voter!"
        )
        message["to"] = to_email
        message["subject"] = "Your CivicIQ Civic Education Summary"

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        service.users().messages().send(
            userId="me",
            body={"raw": raw},
        ).execute()

        return {"status": "success", "message": f"Summary sent to {to_email}"}
    except Exception as e:
        return {"error": str(e), "service": "Gmail"}