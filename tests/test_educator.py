import unittest

from modules.educator import get_topics, validate_question, build_education_prompt


class TestEducatorModule(unittest.TestCase):
    def test_get_topics_returns_list(self):
        topics = get_topics()
        self.assertIsInstance(topics, list)
        self.assertGreater(len(topics), 0)

    def test_validate_civic_question(self):
        self.assertTrue(validate_question("How does voting work?"))
        self.assertTrue(validate_question("What is an election?"))
        self.assertTrue(validate_question("Tell me about democracy"))
        self.assertTrue(validate_question("How are ballots counted?"))

    def test_reject_non_civic_question(self):
        self.assertFalse(validate_question("What is the recipe for pasta?"))
        self.assertFalse(validate_question("Tell me a joke"))
        self.assertFalse(validate_question("What is 2 + 2?"))

    def test_build_prompt_includes_question(self):
        prompt = build_education_prompt("How does voting work?")
        self.assertIn("How does voting work?", prompt)

    def test_build_prompt_includes_language(self):
        prompt = build_education_prompt("What is an election?", language="Hindi")
        self.assertIn("Hindi", prompt)

    def test_build_prompt_default_language_english(self):
        prompt = build_education_prompt("What is democracy?")
        self.assertIn("English", prompt)


if __name__ == "__main__":
    unittest.main()