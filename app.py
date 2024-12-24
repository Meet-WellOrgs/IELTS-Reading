from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient
from flask_cors import CORS
from band import get_band_descriptions  # Import band descriptors

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS to allow frontend requests

# MongoDB Connection
client = MongoClient("mongodb+srv://admin:admin123@scholarai.8hlxeh7.mongodb.net/test?retryWrites=true&w=majority&appName=ScholarAI")  # MongoDB URL
db = client["reading"]  # Database name
collection = db["testing"]  # Collection name

@app.route('/')
def index():
    """
    Serve the main HTML page.
    """
    return render_template("index.html")

@app.route('/api/exam_sets', methods=['GET'])
def get_exam_sets():
    """
    Fetch exam sets (questions and content) from MongoDB.
    """
    try:
        data = list(collection.find({}))  # Fetch all documents
        for item in data:
            item['_id'] = str(item['_id'])  # Convert ObjectId to string for JSON compatibility
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch exam data: {str(e)}"}), 500

# @app.route('/submit', methods=['POST'])
# def submit_answers():
#     """
#     Handle the submission of user answers, compare them with correct answers,
#     and return evaluated results in the same order as presented.
#     """
#     try:
#         # Get JSON data from the frontend
#         user_data = request.get_json()
#         user_answers = user_data.get('answers', {})
#         question_order = user_data.get('question_order', [])  # Original question order from the frontend

#         # Fetch exam data to validate answers
#         exam_data = list(collection.find({}))
#         correct_answers = {}

#         # Extract all questions and their correct answers
#         for exam_set in exam_data:
#             for passage in exam_set.get("passages", []):
#                 for question_group in passage.get("questions", {}).values():
#                     for item in question_group.get("items", []):
#                         question_text = item["question"]
#                         correct_answers[question_text] = {
#                             "correct_answer": item["answer"],
#                             "type": question_group["question_type"],
#                             "suggestion": f"Consider re-reading the passage about '{question_text}'. Focus on understanding key details to refine your answer."
#                         }

#         # Evaluate answers based on the original question order
#         results = []
#         incorrect_count = 0
#         unanswered_count = 0
#         correct_count = 0
#         answered_questions = []
#         unanswered_questions = []

#         for idx, question_text in enumerate(question_order, start=1):
#             question_data = correct_answers.get(question_text, {})
#             question_type = question_data.get("type", "Unknown")

#             # Exclude "Diagram Labelling" questions from results
#             if question_type == "Diagram Labelling":
#                 continue

#             correct_answer = question_data.get("correct_answer", "").strip()
#             suggestion = question_data.get("suggestion", "")
#             user_answer = user_answers.get(question_text, "").strip()

#             if not user_answer:  # Count unanswered questions
#                 unanswered_count += 1
#                 unanswered_questions.append(question_text)
#                 results.append({
#                     "number": idx,
#                     "question": question_text,
#                     "type": question_type,
#                     "user_answer": None,
#                     "correct_answer": correct_answer,
#                     "is_correct": False,
#                     "suggestion": suggestion
#                 })
#                 continue

#             # Mark as answered
#             answered_questions.append(question_text)

#             is_correct = user_answer.lower() == correct_answer.lower()

#             if is_correct:
#                 correct_count += 1
#             else:
#                 incorrect_count += 1

#             results.append({
#                 "number": idx,
#                 "question": question_text,
#                 "type": question_type,
#                 "user_answer": user_answer,
#                 "correct_answer": correct_answer,
#                 "is_correct": is_correct,
#                 "suggestion": suggestion if not is_correct else ""
#             })

#         # Calculate band score
#         total_questions = len(results)
#         band_score = calculate_band_score(correct_count, total_questions)

#         # Get band descriptions
#         band_info = get_band_descriptions(band_score)

#         return jsonify({
#             "results": results,
#             "answered_questions": answered_questions,
#             "unanswered_questions": unanswered_questions,
#             "correct_count": correct_count,
#             "incorrect_count": incorrect_count,
#             "band_score": band_score,
#             "skill_level": band_info["Skill Level"],
#             "description": band_info["Description"]
#         }), 200
#     except Exception as e:
#         return jsonify({"error": f"Failed to process answers: {str(e)}"}), 500

@app.route('/submit', methods=['POST'])
def submit_answers():
    """
    Handle the submission of user answers, compare them with correct answers,
    and return evaluated results in the same order as presented.
    """
    try:
        user_data = request.get_json()
        user_answers = user_data.get('answers', {})
        question_order = user_data.get('question_order', [])

        exam_data = list(collection.find({}))
        correct_answers = {}

        for exam_set in exam_data:
            for passage in exam_set.get("passages", []):
                for question_group in passage.get("questions", {}).values():
                    for item in question_group.get("items", []):
                        question_text = item["question"]
                        correct_answers[question_text] = {
                            "correct_answer": item["answer"],
                            "type": question_group["question_type"],
                            "suggestion": f"Review the diagram or text associated with '{question_text}'."
                        }

        results = []
        incorrect_count = 0
        unanswered_count = 0
        correct_count = 0
        answered_questions = []
        unanswered_questions = []

        for idx, question_text in enumerate(question_order, start=1):
            question_data = correct_answers.get(question_text, {})
            question_type = question_data.get("type", "Unknown")
            correct_answer = question_data.get("correct_answer", "").strip()
            suggestion = question_data.get("suggestion", "")
            user_answer = user_answers.get(question_text, "").strip()

            if not user_answer:
                unanswered_count += 1
                unanswered_questions.append(question_text)
                results.append({
                    "number": idx,
                    "question": question_text,
                    "type": question_type,
                    "user_answer": None,
                    "correct_answer": correct_answer,
                    "is_correct": False,
                    "suggestion": suggestion
                })
                continue

            answered_questions.append(question_text)
            is_correct = user_answer.lower() == correct_answer.lower()

            if is_correct:
                correct_count += 1
            else:
                incorrect_count += 1

            results.append({
                "number": idx,
                "question": question_text,
                "type": question_type,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "suggestion": suggestion if not is_correct else ""
            })

        total_questions = len(results)
        band_score = calculate_band_score(correct_count, total_questions)
        band_info = get_band_descriptions(band_score)

        return jsonify({
            "results": results,
            "answered_questions": answered_questions,
            "unanswered_questions": unanswered_questions,
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "band_score": band_score,
            "skill_level": band_info["Skill Level"],
            "description": band_info["Description"]
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to process answers: {str(e)}"}), 500


def calculate_band_score(correct_count, total_questions):
    """
    Calculate the band score as a proportional value based on the number of correct answers.
    Band score scales from 0 to 9.
    """
    if total_questions == 0:  # Handle edge case with no questions
        return 0
    band_score = (correct_count / total_questions) * 9
    return round(band_score)  # Round to the nearest integer

if __name__ == "__main__":
    app.run(debug=True)
