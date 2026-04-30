import unittest
from unittest.mock import patch


class TestCalendarService(unittest.TestCase):
    @patch("services.calendar_service.get_calendar_service")
    def test_add_election_reminder_success(self, mock_get_calendar_service):
        mock_get_calendar_service.return_value.events.return_value.insert.return_value.execute.return_value = {
            "id": "event-123"
        }

        from services.calendar_service import add_election_reminder

        result = add_election_reminder(
            "Election Day",
            "2025-01-01",
            "Voting reminder",
        )
        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")

    @patch("services.calendar_service.get_calendar_service")
    def test_get_upcoming_civic_events_empty(self, mock_get_calendar_service):
        mock_get_calendar_service.return_value.events.return_value.list.return_value.execute.return_value = {
            "items": []
        }

        from services.calendar_service import get_upcoming_civic_events

        result = get_upcoming_civic_events()
        self.assertIn("message", result)


if __name__ == "__main__":
    unittest.main()