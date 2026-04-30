import unittest

from modules.educator import validate_question


class TestAgentBehavior(unittest.TestCase):
    def test_off_topic_prompts_are_rejected(self):
        """Non-civic prompts should fail the validator gate."""
        off_topic = [
            "What should I cook for dinner?",
            "Tell me about space travel",
            "Write me a poem",
            "What is the stock market?",
        ]
        for prompt in off_topic:
            self.assertFalse(
                validate_question(prompt),
                f"Should have rejected: {prompt}",
            )

    def test_civic_prompts_are_accepted(self):
        """Civic prompts should pass the validator gate."""
        civic = [
            "How does the election process work?",
            "What is voter registration?",
            "Explain the democratic voting system",
            "How are ballots counted?",
            "What is a polling station?",
        ]
        for prompt in civic:
            self.assertTrue(
                validate_question(prompt),
                f"Should have accepted: {prompt}",
            )

    def test_edge_case_empty_string(self):
        self.assertFalse(validate_question(""))

    def test_edge_case_very_long_input(self):
        long_input = "vote " * 500
        self.assertTrue(validate_question(long_input))


if __name__ == "__main__":
    unittest.main()