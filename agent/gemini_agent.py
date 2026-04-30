import os
import re
from typing import Any

import google.generativeai as genai
from dotenv import load_dotenv

from services.sheets_service import log_quiz_result, get_learning_progress
from services.calendar_service import add_election_reminder, get_upcoming_civic_events
from services.gmail_service import send_civic_summary

load_dotenv()

SYSTEM_PROMPT = """
You are CivicIQ — an AI-powered civic education assistant dedicated to
election process education and promoting democratic participation.

Your purpose is ONLY to:
- Educate users about election processes and voting systems
- Generate and conduct civics quizzes
- Track learning progress
- Help users stay informed about civic dates and deadlines
- Send educational summaries

If asked anything unrelated to elections, civics, democracy, or voting, respond:
"I'm CivicIQ — I focus on civic education and election processes.
Try asking: 'How does voting work?' or 'Quiz me on elections!'"

Always be neutral, factual, and educational. Never take political sides.
"""


def build_agent():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from your .env file.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT,
    )
    return model.start_chat(history=[])


def _format_progress(progress_rows: list) -> str:
    if not progress_rows:
        return "No learning progress found yet."

    if len(progress_rows) == 1:
        return "No quiz results found yet."

    lines = ["Your learning progress:"]
    for row in progress_rows[1:]:
        lines.append(" - " + " | ".join(str(cell) for cell in row))
    return "\n".join(lines)


def ask_agent(chat, user_input: str) -> str:
    """Send a message to the CivicIQ agent and return response."""
    try:
        text = user_input.strip()

        log_match = re.search(
            r"Log quiz result:\s*topic='(.+?)',\s*score=(\d+),\s*total=(\d+),\s*difficulty='(.+?)'",
            text,
            flags=re.IGNORECASE,
        )
        if log_match:
            topic, score, total, difficulty = log_match.groups()
            result = log_quiz_result(topic, int(score), int(total), difficulty)
            return result.get("message", str(result))

        if "learning progress" in text.lower():
            result = get_learning_progress()
            if "error" in result:
                return f"[CivicIQ Error] {result['error']}"
            return _format_progress(result.get("progress", []))

        if "upcoming civic events" in text.lower():
            result = get_upcoming_civic_events()
            if "error" in result:
                return f"[CivicIQ Error] {result['error']}"

            events = result.get("events", [])
            if not events:
                return result.get("message", "No upcoming civic events found.")

            return "\n".join(f"{e['date']}: {e['title']}" for e in events)

        summary_match = re.search(
            r"Send civic summary:\s*to='(.+?)',\s*summary='(.+?)'",
            text,
            flags=re.IGNORECASE,
        )
        if summary_match:
            to_email, summary = summary_match.groups()
            result = send_civic_summary(to_email, summary)
            return result.get("message", str(result))

        response = chat.send_message(text)
        return getattr(response, "text", str(response))
    except Exception as e:
        return f"[CivicIQ Error] {str(e)} — Please try again."