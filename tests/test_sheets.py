import unittest
from unittest.mock import patch

from services.cache import get_cached, set_cached, clear_cache


class TestCacheService(unittest.TestCase):
    def setUp(self):
        clear_cache()

    def test_set_and_get_cache(self):
        set_cached("test_key", {"data": "value"})
        result = get_cached("test_key")
        self.assertEqual(result, {"data": "value"})

    def test_missing_key_returns_none(self):
        result = get_cached("nonexistent_key")
        self.assertIsNone(result)

    def test_clear_cache(self):
        set_cached("key1", "value1")
        clear_cache()
        self.assertIsNone(get_cached("key1"))


class TestSheetsService(unittest.TestCase):
    @patch("services.sheets_service.get_sheets_service")
    @patch("services.sheets_service.get_or_create_sheet", return_value="fake_sheet_id")
    def test_log_quiz_result_success(self, mock_get_or_create_sheet, mock_get_sheets_service):
        mock_get_sheets_service.return_value.spreadsheets.return_value.values.return_value.append.return_value.execute.return_value = {}

        from services.sheets_service import log_quiz_result

        result = log_quiz_result("voting", 3, 3, "beginner")
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)

    @patch("services.sheets_service.get_sheets_service")
    def test_log_quiz_result_returns_dict(self, mock_get_sheets_service):
        mock_get_sheets_service.side_effect = Exception("No credentials in test")

        from services.sheets_service import log_quiz_result

        result = log_quiz_result("voting", 2, 3, "beginner")
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()