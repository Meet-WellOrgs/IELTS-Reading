import streamlit as st
import pymongo
from pymongo import MongoClient
from band import get_band_descriptions

# MongoDB Connection
client = MongoClient("mongodb+srv://admin:admin123@scholarai.8hlxeh7.mongodb.net/test?retryWrites=true&w=majority&appName=ScholarAI")
db = client["reading"]
collection = db["testing"]

st.set_page_config(page_title="Reading Exam Portal", layout="wide", page_icon="📖")

# CSS Styling
st.markdown(
    """
    <style>
    body {
        font-family: 'Roboto', sans-serif;
        background: linear-gradient(to right, #f3f4f7, #e3e8ef);
    }
    header {
        background: linear-gradient(to right, #1e3c72, #2a5298);
        color: white;
        text-align: center;
        padding: 3rem 1rem;
        font-size: 2.5rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    .question-box {
        margin: 20px 0;
        padding: 20px;
        background: #f9f9f9;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    .image-section img {
        max-width: 100%;
        height: auto;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown('<header>📖 Reading Exam Portal</header>', unsafe_allow_html=True)

def fetch_exam_data():
    """Fetch exam data from MongoDB."""
    try:
        data = list(collection.find({}))
        for item in data:
            item['_id'] = str(item['_id'])  # Convert ObjectId to string
        return data
    except Exception as e:
        st.error(f"Error fetching exam data: {str(e)}")
        return []

def evaluate_answers(user_answers, question_order, exam_data):
    """Evaluate the answers submitted by the user."""
    correct_answers = {}
    for exam_set in exam_data:
        for passage in exam_set.get("passages", []):
            for question_group in passage.get("questions", {}).values():
                for item in question_group.get("items", []):
                    question_text = item["question"]
                    correct_answers[question_text] = {
                        "correct_answer": item["answer"],
                        "type": question_group["question_type"],
                        "suggestion": f"Review the diagram or text associated with '{question_text}'.",
                    }

    results = []
    correct_count = incorrect_count = unanswered_count = 0
    for idx, question in enumerate(question_order, start=1):
        user_answer = user_answers.get(question, "").strip()
        correct_data = correct_answers.get(question, {})
        correct_answer = correct_data.get("correct_answer", "").strip()
        is_correct = user_answer.lower() == correct_answer.lower()

        if not user_answer:
            unanswered_count += 1
        elif is_correct:
            correct_count += 1
        else:
            incorrect_count += 1

        results.append(
            {
                "number": idx,
                "question": question,
                "user_answer": user_answer or "<Not Answered>",
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "type": correct_data.get("type", ""),
                "suggestion": correct_data.get("suggestion", ""),
            }
        )

    total_questions = len(results)
    band_score = round((correct_count / total_questions) * 9) if total_questions else 0
    band_info = get_band_descriptions(band_score)

    return results, band_score, band_info

# Main Application
st.subheader("Exam Section")
exam_data = fetch_exam_data()

if not exam_data:
    st.error("No exam data found!")
else:
    question_order = []
    user_answers = {}
    submitted = False

    for exam_set in exam_data:
        for passage in exam_set.get("passages", []):
            st.markdown(f"## {passage['title']}")
            st.write(passage.get("content", "No content available."))

            # Display diagram-based questions
            if "image_based" in passage.get("questions", {}):
                st.markdown("### Diagram Labelling")
                st.image(
                    "https://websitecmscdn.s3.ap-south-1.amazonaws.com/school_experiment_diagram_labelling_exercise_1_6a9576f532.PNG"
                )
                for idx, item in enumerate(passage["questions"]["image_based"]["items"]):
                    question_key = f"image_{idx}"  # Unique key for each question
                    question_order.append(item["question"])
                    user_answers[item["question"]] = st.selectbox(
                        f"{item['question']}", options=item["options"], key=question_key
                    )

            # Display other question groups
            for question_group in passage.get("questions", {}).values():
                if question_group["question_type"] != "Diagram Labelling":
                    st.markdown(f"### {question_group['question_type']}")
                    for idx, item in enumerate(question_group["items"]):
                        question_key = f"question_{item['question']}_{idx}"  # Unique key
                        question_order.append(item["question"])
                        if question_group["question_type"] == "Multiple Choice Questions":
                            user_answers[item["question"]] = st.radio(
                                f"{item['question']}", options=item["options"], key=question_key
                            )
                        else:
                            user_answers[item["question"]] = st.text_area(
                                f"{item['question']}", key=question_key
                            )

    # Submit Button
    if st.button("Submit Answers"):
        submitted = True

    # Results Section
    if submitted:
        results, band_score, band_info = evaluate_answers(user_answers, question_order, exam_data)

        st.markdown("## Results")
        for result in results:
            st.markdown(f"### Question {result['number']}")
            st.write(f"**Question:** {result['question']}")
            st.write(f"**Your Answer:** {result['user_answer']}")
            st.write(f"**Correct Answer:** {result['correct_answer']}")
            st.write("✅ **Correct**" if result["is_correct"] else "❌ **Incorrect**")
            if not result["is_correct"]:
                st.write(f"**Suggestion:** {result['suggestion']}")

        st.markdown("## Summary")
        st.markdown(f"**Total Questions:** {len(results)}")
        st.markdown(f"**Answered:** {len([r for r in results if r['user_answer'] != '<Not Answered>'])}")
        st.markdown(f"**Unanswered:** {len([r for r in results if r['user_answer'] == '<Not Answered>'])}")
        st.markdown(f"**Correct Answers:** {sum(1 for r in results if r['is_correct'])}")
        st.markdown(f"**Incorrect Answers:** {sum(1 for r in results if not r['is_correct'])}")
        st.markdown(f"**Your Band Score:** {band_score}")
        st.write(f"**Skill Level:** {band_info['Skill Level']}")
        st.write(f"**Description:** {band_info['Description']}")

        if st.button("Retake Test"):
            st.experimental_rerun()
