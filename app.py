import streamlit as st

from data.syllabus import CBSE_9, SOF_9, LESSON_STEPS
from services.tutor import generate_step_lesson, answer_doubt
from services.quiz import generate_quiz
from services.progress import get_current_step, save_current_step, mark_completed
from services.llm import generate_speech

from services.mock_test import (
    generate_olympiad_mock_test,
    generate_cbse_mock_test,
    calculate_score
)

st.set_page_config(
    page_title="Grade 9 CBSE AI Tutor",
    page_icon="📚",
    layout="wide"
)

USERS = {
    "parent": "parent123",
    "student": "student123"
}

import os
from services.ocr import extract_text_from_image


def login_page():
    st.title("🔐 Login - Grade 9 CBSE AI Tutor")
    st.markdown("### Welcome to the AI Learning Platform")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("✅ Login successful")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")


def logout_button():
    with st.sidebar:
        st.write(f"👤 Logged in as: **{st.session_state.get('username')}**")

        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.rerun()


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "username" not in st.session_state:
    st.session_state["username"] = None

if not st.session_state["logged_in"]:
    login_page()
    st.stop()

logout_button()

st.title("📚 Grade 9 CBSE + SOF Olympiad AI Tutor")

st.markdown("""
Welcome to the AI-powered tutor platform for:

- CBSE Grade 9
- SOF Olympiads
- Science
- Maths
- English
- Social Science
- Hindi

Choose a learning mode from the sidebar.
""")

mode = st.sidebar.radio(
    "Choose Learning Mode",
    ["CBSE Chapter Tutor", "SOF Olympiad Tutor"]
)

if mode == "CBSE Chapter Tutor":
    subject = st.sidebar.selectbox("Select Subject", list(CBSE_9.keys()))
    chapter = st.sidebar.selectbox("Select Chapter", CBSE_9[subject])
else:
    subject = st.sidebar.selectbox("Select Olympiad", list(SOF_9.keys()))
    chapter = st.sidebar.selectbox("Select Section", SOF_9[subject])


tab1, tab2, tab3, tab4 = st.tabs([
    "📖 Lesson",
    "❓ Ask Doubt",
    "📝 Quiz",
    "🧪 Mock Test"
])


# =========================================================
# TAB 1 - STEP-WISE LESSON GENERATOR
# =========================================================
with tab1:
    st.subheader("📖 Step-by-Step Guided Lesson")

    username = st.session_state.get("username", "student")

    default_steps = [
        "Concept introduction",
        "Core explanation",
        "Worked examples",
        "Practice questions",
        "Revision and recap"
    ]

    subject_steps = LESSON_STEPS.get(subject, {})
    steps = subject_steps.get(chapter, default_steps)

    saved_step = get_current_step(username, mode, subject, chapter)

    step_key = f"lesson_step_{username}_{mode}_{subject}_{chapter}"
    lesson_key = f"lesson_text_{username}_{mode}_{subject}_{chapter}"
    audio_key = f"lesson_audio_{username}_{mode}_{subject}_{chapter}"

    if step_key not in st.session_state:
        st.session_state[step_key] = saved_step

    current_step = st.session_state[step_key]

    if current_step >= len(steps):
        current_step = 0
        st.session_state[step_key] = 0
        save_current_step(username, mode, subject, chapter, 0)

    st.progress((current_step + 1) / len(steps))

    st.write(f"### Subject: {subject}")
    st.write(f"### Chapter/Topic: {chapter}")
    st.write(f"### Step {current_step + 1} of {len(steps)}")
    st.info(f"Current Learning Step: **{steps[current_step]}**")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⬅ Previous") and current_step > 0:
            st.session_state[step_key] -= 1
            save_current_step(username, mode, subject, chapter, st.session_state[step_key])
            st.session_state.pop(lesson_key, None)
            st.session_state.pop(audio_key, None)
            st.rerun()

    with col2:
        if st.button("✅ Mark Step Complete"):
            if current_step < len(steps) - 1:
                st.session_state[step_key] += 1
                save_current_step(username, mode, subject, chapter, st.session_state[step_key])
                st.session_state.pop(lesson_key, None)
                st.session_state.pop(audio_key, None)
                st.rerun()
            else:
                mark_completed(username, mode, subject, chapter)
                st.success("🎉 Chapter completed!")

    with col3:
        if st.button("🔄 Restart Chapter"):
            st.session_state[step_key] = 0
            save_current_step(username, mode, subject, chapter, 0)
            st.session_state.pop(lesson_key, None)
            st.session_state.pop(audio_key, None)
            st.rerun()

    if st.button("Generate This Step Lesson"):
        with st.spinner("Generating focused lesson..."):
            lesson = generate_step_lesson(
                subject,
                chapter,
                mode,
                steps[current_step]
            )
            st.session_state[lesson_key] = lesson
            st.session_state.pop(audio_key, None)

    if lesson_key in st.session_state:
        lesson = st.session_state[lesson_key]
        st.markdown(lesson)

        if st.button("🔊 Read Aloud"):
            with st.spinner("Generating audio..."):
                audio_file = generate_speech(lesson)
                with open(audio_file, "rb") as audio:
                    st.session_state[audio_key] = audio.read()

        if audio_key in st.session_state:
            st.audio(st.session_state[audio_key], format="audio/mp3")
    else:
        st.warning("Click **Generate This Step Lesson** to start or resume this lesson step.")


# =========================================================
# TAB 2 - ASK DOUBT
# =========================================================
with tab2:
    st.subheader("❓ Ask Your Doubt")

    doubt = st.text_area("Type your question here")

    if st.button("Explain Doubt"):
        if doubt.strip() == "":
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                answer = answer_doubt(subject, chapter, doubt)
                st.markdown(answer)


# =========================================================
# TAB 3 - QUIZ
# =========================================================
with tab3:
    st.subheader("📝 Practice Quiz")

    difficulty = st.selectbox(
        "Select Difficulty",
        ["Easy", "Medium", "Hard", "Olympiad HOTS"],
        key="quiz_difficulty"
    )

    count = st.slider(
        "Number of Questions",
        3,
        15,
        5,
        key="quiz_count"
    )

    if st.button("Generate Quiz"):
        with st.spinner("Creating quiz..."):
            quiz = generate_quiz(subject, chapter, mode, difficulty, count)
            st.markdown(quiz)


# =========================================================
# TAB 4 - MOCK TEST
# =========================================================
with tab4:

    st.subheader("🧪 AI Mock Test Generator")

    mock_type = st.radio(
        "Choose Test Type",
        [
            "CBSE Exam Mock Test",
            "SOF Olympiad Mock Test"
        ]
    )

    mock_difficulty = st.selectbox(
        "Select Difficulty",
        ["Easy", "Medium", "Hard", "Olympiad HOTS"],
        key="mock_difficulty"
    )

    mock_count = st.slider(
        "Number of Questions",
        5,
        30,
        10,
        key="mock_count"
    )

    if mock_type == "CBSE Exam Mock Test":

        exam_type = st.selectbox(
            "Exam Type",
            [
                "Class Test",
                "Mid Term",
                "Annual Exam"
            ]
        )

    mock_state_key = "mock_test_questions"

    if mock_state_key not in st.session_state:
        st.session_state[mock_state_key] = []

    if st.button("Generate Mock Test"):

        with st.spinner("Generating mock test..."):

            if mock_type == "SOF Olympiad Mock Test":

                questions = generate_olympiad_mock_test(
                    olympiad=subject,
                    num_questions=mock_count,
                    difficulty=mock_difficulty
                )

            else:

                questions = generate_cbse_mock_test(
                    subject=subject,
                    chapter=chapter,
                    exam_type=exam_type,
                    num_questions=mock_count,
                    difficulty=mock_difficulty
                )

            st.session_state[mock_state_key] = questions

            for key in list(st.session_state.keys()):
                if str(key).startswith("mock_answer_"):
                    del st.session_state[key]

    questions = st.session_state.get(mock_state_key, [])

    if not questions:
        st.info("Generate a mock test to begin.")
    else:

        user_answers = {}

        for q in questions:

            qid = str(q.get("id"))
            options = q.get("options", {})

            st.markdown(f"### Q{qid}. {q.get('question')}")

            st.caption(
                f"Section: {q.get('section', 'General')} | "
                f"Marks: {q.get('marks', 1)}"
            )

            selected = st.radio(
                "Choose answer",
                list(options.keys()),
                format_func=lambda x, opts=options: f"{x}. {opts[x]}",
                key=f"mock_answer_{qid}"
            )

            user_answers[qid] = selected

            st.markdown("---")

        if st.button("Submit Mock Test"):

            total_score, max_score, results = calculate_score(
                questions,
                user_answers
            )

            st.success(
                f"🎯 Final Score: {total_score} / {max_score}"
            )

            st.subheader("📘 Detailed Review")

            for result in results:

                if result["is_correct"]:
                    st.success(f"Q{result['id']}: Correct")
                else:
                    st.error(f"Q{result['id']}: Incorrect")

                options = result.get("options", {})

                selected = result.get("selected")
                correct = result.get("correct")

                selected_text = options.get(selected, "Not answered")
                correct_text = options.get(correct, "")

                st.write(
                    f"Your Answer: **{selected}. {selected_text}**"
                )

                st.write(
                    f"Correct Answer: **{correct}. {correct_text}**"
                )

                st.write(
                    f"Explanation: {result.get('explanation', '')}"
                )

                st.markdown("---")


st.markdown("---")
st.caption("© 2026 Grade 9 CBSE + SOF Olympiad AI Tutor, Created by PB for AB")
