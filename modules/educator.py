ELECTION_TOPICS = [
    "How does the voting process work?",
    "What is the Electoral College?",
    "What are the different types of voting systems?",
    "How are election results counted and verified?",
    "What is gerrymandering?",
    "How do referendums and ballots work?",
    "What is voter registration and why does it matter?",
    "How does campaign finance work?",
    "What are exit polls?",
    "How does ranked-choice voting work?",
]


def get_topics() -> list:
    """Returns list of available civic education topics."""
    return ELECTION_TOPICS


def build_education_prompt(question: str, language: str = "English") -> str:
    """Builds a civic education prompt for Gemini."""
    return f"""
You are CivicIQ, a civic education assistant helping citizens understand
election processes and democratic participation.

Answer the following question clearly and educationally in {language}.
Focus on facts, be neutral, and make it accessible to any citizen.
End with one follow-up question to encourage deeper learning.

Question: {question}
"""


def validate_question(question: str) -> bool:
    """Check if a question is relevant to civic/election education."""
    civic_keywords = [
        "vote",
        "voting",
        "election",
        "elections",
        "democracy",
        "democratic",
        "candidate",
        "ballot",
        "ballots",
        "civic",
        "government",
        "parliament",
        "constitution",
        "political",
        "citizen",
        "referendum",
        "campaign",
        "party",
        "polling",
        "electoral",
        "evm",
        "representative",
        "constituency",
        "manifest",
        "president",
        "senate",
    ]

    text = question.lower()
    return any(keyword in text for keyword in civic_keywords)