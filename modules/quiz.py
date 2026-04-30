import json
import re

DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced"]


def build_quiz_prompt(topic: str, difficulty: str, num_questions: int = 3) -> str:
    """Builds a prompt asking Gemini to generate a quiz."""
    return f"""
Generate a {difficulty}-level civic education quiz about:
"{topic}"

Create exactly {num_questions} multiple choice questions.
Respond ONLY with valid JSON in this exact format, nothing else:

{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
      "correct": "A",
      "explanation": "Why this is correct"
    }}
  ]
}}
"""


def parse_quiz_response(raw_response: str) -> dict:
    """Safely parse Gemini's quiz JSON response."""
    try:
        clean = raw_response.strip()

        if clean.startswith("```"):
            clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.IGNORECASE)
            clean = re.sub(r"\s*```$", "", clean)

        return json.loads(clean.strip())
    except Exception as e:
        return {"error": f"Could not parse quiz: {str(e)}", "questions": []}


def calculate_score(answers: list, correct_answers: list) -> dict:
    """Calculate quiz score and return feedback."""
    score = sum(
        1 for u, c in zip(answers, correct_answers)
        if str(u).strip().upper() == str(c).strip().upper()
    )
    total = len(correct_answers)
    percentage = (score / total * 100) if total > 0 else 0

    if percentage >= 80:
        feedback = "Excellent! You have strong civic knowledge. 🏆"
        next_difficulty = "advanced"
    elif percentage >= 50:
        feedback = "Good effort! Keep learning to strengthen your civic awareness. 📚"
        next_difficulty = "intermediate"
    else:
        feedback = "Keep studying! Understanding elections is key to democracy."
        next_difficulty = "beginner"

    return {
        "score": score,
        "total": total,
        "percentage": round(percentage, 1),
        "feedback": feedback,
        "next_difficulty": next_difficulty,
    }