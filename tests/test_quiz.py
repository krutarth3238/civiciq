import unittest

from modules.quiz import (
    build_quiz_prompt,
    parse_quiz_response,
    calculate_score,
    DIFFICULTY_LEVELS,
)


class TestQuizModule(unittest.TestCase):
    def test_difficulty_levels_exist(self):
        self.assertIn("beginner", DIFFICULTY_LEVELS)
        self.assertIn("intermediate", DIFFICULTY_LEVELS)
        self.assertIn("advanced", DIFFICULTY_LEVELS)

    def test_build_quiz_prompt_returns_string(self):
        result = build_quiz_prompt("voting", "beginner", 3)
        self.assertIsInstance(result, str)
        self.assertIn("voting", result)
        self.assertIn("beginner", result)

    def test_parse_valid_quiz_json(self):
        valid_json = '{"questions": [{"question": "Q?", "options": ["A) a", "B) b", "C) c", "D) d"], "correct": "A", "explanation": "Because A"}]}'
        result = parse_quiz_response(valid_json)
        self.assertIn("questions", result)
        self.assertEqual(len(result["questions"]), 1)

    def test_parse_invalid_json_returns_error(self):
        result = parse_quiz_response("this is not json at all")
        self.assertIn("error", result)

    def test_parse_json_with_markdown_fences(self):
        fenced = '```json\n{"questions": []}\n```'
        result = parse_quiz_response(fenced)
        self.assertIn("questions", result)

    def test_calculate_score_perfect(self):
        result = calculate_score(["A", "B", "C"], ["A", "B", "C"])
        self.assertEqual(result["score"], 3)
        self.assertEqual(result["percentage"], 100.0)

    def test_calculate_score_zero(self):
        result = calculate_score(["A", "A", "A"], ["B", "B", "B"])
        self.assertEqual(result["score"], 0)

    def test_calculate_score_returns_feedback(self):
        result = calculate_score(["A"], ["A"])
        self.assertIn("feedback", result)
        self.assertIn("next_difficulty", result)

    def test_calculate_score_empty(self):
        result = calculate_score([], [])
        self.assertEqual(result["percentage"], 0)


if __name__ == "__main__":
    unittest.main()