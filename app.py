from agent.gemini_agent import build_agent, ask_agent
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from modules.educator import get_topics, validate_question, build_education_prompt
from modules.quiz import build_quiz_prompt, parse_quiz_response, calculate_score
from services.sheets_service import log_quiz_result, get_learning_progress
from services.calendar_service import add_election_reminder
from services.gmail_service import send_civic_summary

load_dotenv()

app = Flask(__name__)
CORS(app)

# ─── ROUTES ───────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "CivicIQ API is running"})


@app.route('/api/topics', methods=['GET'])
def topics():
    return jsonify({"topics": get_topics()})


@app.route('/api/learn', methods=['POST'])
def learn():
    data = request.get_json()
    question = data.get('question', '').strip()
    language = data.get('language', 'English')

    if not question:
        return jsonify({"error": "Question is required"}), 400

    if not validate_question(question):
        return jsonify({
            "response": "I focus only on civic education and election processes. "
                        "Try asking: 'How does voting work?' or 'What is an EVM?'"
        })

    try:
        chat = build_agent()
        prompt = build_education_prompt(question, language)
        response = ask_agent(chat, prompt)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/quiz/generate', methods=['POST'])
def quiz_generate():
    data = request.get_json()
    topic = data.get('topic', 'general elections')
    difficulty = data.get('difficulty', 'beginner')
    language = data.get('language', 'English')

    try:
        chat = build_agent()
        prompt = build_quiz_prompt(topic, difficulty, num_questions=3)

        if language != 'English':
            prompt += f"\n\nGenerate all questions and options in {language}."

        raw = ask_agent(chat, prompt)
        quiz_data = parse_quiz_response(raw)

        if "error" in quiz_data:
            return jsonify({"error": quiz_data["error"]}), 500

        return jsonify(quiz_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/quiz/submit', methods=['POST'])
def quiz_submit():
    data = request.get_json()
    topic = data.get('topic', 'general')
    user_answers = data.get('user_answers', [])
    correct_answers = data.get('correct_answers', [])
    difficulty = data.get('difficulty', 'beginner')

    result = calculate_score(user_answers, correct_answers)

    try:
        log_quiz_result(topic, result['score'], result['total'], difficulty)
    except Exception:
        pass

    return jsonify(result)


@app.route('/api/progress', methods=['GET'])
def progress():
    try:
        data = get_learning_progress()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e), "progress": []}), 200


@app.route('/api/calendar/add', methods=['POST'])
def calendar_add():
    data = request.get_json()
    result = add_election_reminder(
        data.get('title'),
        data.get('date'),
        data.get('description', '')
    )
    return jsonify(result)


@app.route('/api/email/summary', methods=['POST'])
def email_summary():
    data = request.get_json()
    result = send_civic_summary(
        data.get('email'),
        data.get('summary')
    )
    return jsonify(result)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)