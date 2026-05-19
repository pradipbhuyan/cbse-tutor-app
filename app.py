import os
from datetime import datetime
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from data.syllabus import CBSE_9, SOF_9, LESSON_STEPS
from services.tutor import generate_step_lesson, answer_doubt
from services.quiz import generate_quiz
from services.progress import get_current_step, save_current_step, mark_completed
from services.llm import generate_speech
from services.mock_test import (
    generate_olympiad_mock_test,
    generate_cbse_mock_test,
    calculate_score,
)
from services.ocr import extract_text_from_image
from data.resources import LEARNING_RESOURCES

# Optional test history support. If the file is not created yet, the app still works.
try:
    from services.test_history import (
        save_test_result,
        get_user_history,
        get_leaderboard,
    )
except Exception:
    def save_test_result(result):
        return None

    def get_user_history(username):
        return []

    def get_leaderboard():
        return []


# -----------------------------
# Streamlit Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Grade 9 CBSE AI Tutor",
    page_icon="📚",
    layout="wide",
)


# -----------------------------
# Users from Streamlit Secrets
# -----------------------------
USERS = {
    "akshita": st.secrets["AKSHITA_PASSWORD"],
    "pradip": st.secrets["PRADIP_PASSWORD"],
    "admin": st.secrets["ADMIN_PASSWORD"],
}


# -----------------------------
# Voice and Teacher Settings
# -----------------------------
VOICE_OPTIONS = {
    "English India Female (Neerja)": "en-IN-NeerjaNeural",
    "English India Male (Prabhat)": "en-IN-PrabhatNeural",
    "Hindi Female (Swara)": "hi-IN-SwaraNeural",
    "Hindi Male (Madhur)": "hi-IN-MadhurNeural",
    "US Female (Aria)": "en-US-AriaNeural",
    "US Male (Guy)": "en-US-GuyNeural",
    "UK Female (Sonia)": "en-GB-SoniaNeural",
    "UK Male (Ryan)": "en-GB-RyanNeural",
}

TEACHER_PERSONAS = {
    "Friendly Teacher": "Explain warmly, patiently, and encouragingly.",
    "Strict Exam Coach": "Focus on exam preparation, accuracy, common mistakes, and scoring.",
    "Slow Step-by-Step Teacher": "Explain slowly, with very small steps and simple examples.",
    "Olympiad Coach": "Focus on reasoning, HOTS, shortcuts, and tricky question patterns.",
    "Storytelling Teacher": "Explain concepts using stories, analogies, and real-life examples.",
}


# -----------------------------
# Login Page
# -----------------------------
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


# -----------------------------
# Logout Button
# -----------------------------
def logout_button():
    with st.sidebar:
        st.write(f"👤 Logged in as: **{st.session_state.get('username')}**")

        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.rerun()


# -----------------------------
# Utility Functions
# -----------------------------
def reset_mock_answers():
    for key in list(st.session_state.keys()):
        if str(key).startswith("mock_answer_"):
            del st.session_state[key]


def show_resource(resource):
    st.markdown(f"### {resource.get('title', 'Learning Resource')}")
    url = resource.get("url", "")
    resource_type = resource.get("type", "website")

    if resource_type == "youtube" and "youtube.com/watch" in url:
        st.video(url)
    else:
        st.markdown(f"[Open Free Resource]({url})")

    st.markdown("---")


def get_resources_for_topic(subject, chapter):
    subject_resources = LEARNING_RESOURCES.get(subject, {})
    chapter_resources = subject_resources.get(chapter, [])

    if chapter_resources:
        return chapter_resources

    search_query = f"Class 9 {subject} {chapter} free lecture"
    youtube_url = "https://www.youtube.com/results?search_query=" + search_query.replace(" ", "+")

    fallback = [
        {
            "title": f"YouTube Search - Free videos for {chapter}",
            "type": "website",
            "url": youtube_url,
        },
        {
            "title": "NCERT Official Textbooks",
            "type": "website",
            "url": "https://ncert.nic.in/textbook.php",
        },
    ]

    if subject == "Science":
        fallback.append({
            "title": "Khan Academy NCERT Class 9 Science",
            "type": "website",
            "url": "https://www.khanacademy.org/science/ncert-class-9-science",
        })
        fallback.append({
            "title": "PhET Free Science Simulations",
            "type": "website",
            "url": "https://phet.colorado.edu/",
        })
    elif subject == "Maths":
        fallback.append({
            "title": "Khan Academy Math",
            "type": "website",
            "url": "https://www.khanacademy.org/math",
        })
    elif subject in ["Science Olympiad", "Maths Olympiad", "English Olympiad"]:
        fallback.append({
            "title": f"Free YouTube Search - Class 9 {subject}",
            "type": "website",
            "url": "https://www.youtube.com/results?search_query=" + f"Class 9 {subject} free preparation".replace(" ", "+"),
        })

    return fallback


# -----------------------------
# Session State Initialization
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "username" not in st.session_state:
    st.session_state["username"] = None

if not st.session_state["logged_in"]:
    login_page()
    st.stop()


# -----------------------------
# Sidebar
# -----------------------------
logout_button()

mode = st.sidebar.radio(
    "Choose Learning Mode",
    ["CBSE Chapter Tutor", "SOF Olympiad Tutor"],
)

if mode == "CBSE Chapter Tutor":
    subject = st.sidebar.selectbox("Select Subject", list(CBSE_9.keys()))
    chapter = st.sidebar.selectbox("Select Chapter", CBSE_9[subject])
else:
    subject = st.sidebar.selectbox("Select Olympiad", list(SOF_9.keys()))
    chapter = st.sidebar.selectbox("Select Section", SOF_9[subject])

selected_voice_name = st.sidebar.selectbox(
    "🔊 Narration Voice",
    list(VOICE_OPTIONS.keys()),
    index=0,
)
selected_voice = VOICE_OPTIONS[selected_voice_name]

speech_rate = st.sidebar.selectbox(
    "Narration Speed",
    ["-25%", "-10%", "+0%", "+10%", "+20%"],
    index=2,
)

speech_pitch = st.sidebar.selectbox(
    "Narration Pitch",
    ["-10Hz", "+0Hz", "+10Hz", "+20Hz"],
    index=1,
)

teacher_persona = st.sidebar.selectbox(
    "👩‍🏫 Teacher Persona",
    list(TEACHER_PERSONAS.keys()),
    index=0,
)


# -----------------------------
# Header
# -----------------------------
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


# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📖 Lesson",
    "❓ Ask Doubt",
    "📝 Quiz",
    "🧪 Mock Test",
    "🎥 Learn More",
    "📊 Analytics",
    "🏆 Leaderboard",
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
        "Revision and recap",
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
                steps[current_step],
                TEACHER_PERSONAS[teacher_persona],
            )
            st.session_state[lesson_key] = lesson
            st.session_state.pop(audio_key, None)

    if lesson_key in st.session_state:
        lesson = st.session_state[lesson_key]
        st.markdown(lesson)

        if st.button("🔊 Read Aloud"):
            with st.spinner("Generating audio..."):
                audio_file = generate_speech(
                    lesson,
                    voice=selected_voice,
                    rate=speech_rate,
                    pitch=speech_pitch,
                )
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
        key="quiz_difficulty",
    )

    count = st.slider(
        "Number of Questions",
        3,
        15,
        5,
        key="quiz_count",
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
        ["CBSE Exam Mock Test", "SOF Olympiad Mock Test"],
    )

    mock_difficulty = st.selectbox(
        "Select Difficulty",
        ["Easy", "Medium", "Hard", "Olympiad HOTS"],
        key="mock_difficulty",
    )

    mock_count = st.slider(
        "Number of Questions",
        5,
        30,
        10,
        key="mock_count",
    )

    exam_type = "Class Test"
    if mock_type == "CBSE Exam Mock Test":
        exam_type = st.selectbox(
            "Exam Type",
            ["Class Test", "Mid Term", "Annual Exam"],
        )

    st.markdown("### Test Controls")

    enable_timer = st.checkbox("Enable Timer", value=True)

    test_minutes = st.slider(
        "Test Duration in Minutes",
        5,
        120,
        30,
    )

    negative_marking = st.checkbox("Enable Negative Marking", value=False)

    negative_marks = st.selectbox(
        "Negative Marks Per Wrong Answer",
        [0, 0.25, 0.5, 1.0],
        index=1,
    )

    mock_state_key = "mock_test_questions"
    submitted_key = "mock_test_submitted"
    results_key = "mock_test_results"
    start_time_key = "mock_start_time"

    if mock_state_key not in st.session_state:
        st.session_state[mock_state_key] = []

    if submitted_key not in st.session_state:
        st.session_state[submitted_key] = False

    if st.button("Generate Mock Test"):
        with st.spinner("Generating mock test..."):
            if mock_type == "SOF Olympiad Mock Test":
                questions = generate_olympiad_mock_test(
                    olympiad=subject,
                    num_questions=mock_count,
                    difficulty=mock_difficulty,
                )
            else:
                questions = generate_cbse_mock_test(
                    subject=subject,
                    chapter=chapter,
                    exam_type=exam_type,
                    num_questions=mock_count,
                    difficulty=mock_difficulty,
                )

            st.session_state[mock_state_key] = questions
            st.session_state["mock_start_time"] = datetime.now().isoformat()
            st.session_state[submitted_key] = False
            st.session_state.pop(results_key, None)
            st.session_state[start_time_key] = datetime.now().isoformat()
            reset_mock_answers()

    questions = st.session_state.get(mock_state_key, [])

    if enable_timer and "mock_start_time" in st.session_state:

        st_autorefresh(interval=1000, key="mock_timer_refresh")
    
        start_time = datetime.fromisoformat(
            st.session_state["mock_start_time"]
        )
    
        elapsed_seconds = int(
            (datetime.now() - start_time).total_seconds()
        )
    
        remaining_seconds = max(
            0,
            test_minutes * 60 - elapsed_seconds
        )
    
        remaining_minutes = remaining_seconds // 60
        remaining_secs = remaining_seconds % 60
    
        st.info(
            f"⏱️ Time remaining: "
            f"{remaining_minutes:02d}:{remaining_secs:02d}"
        )
    
        if remaining_seconds <= 0:
            st.error("⏰ Time is over. Submit your test.")

    if not questions:
        st.info("Generate a mock test to begin.")
    else:
        if start_time_key in st.session_state:
            start_time = datetime.fromisoformat(st.session_state[start_time_key])
            elapsed_seconds = int((datetime.now() - start_time).total_seconds())
            elapsed_minutes = elapsed_seconds // 60
            st.info(f"Time elapsed: {elapsed_minutes} minutes")

            if enable_timer and elapsed_minutes >= test_minutes:
                st.warning("Time is over. Please submit your test.")

        user_answers = {}

        for q in questions:
            qid = str(q.get("id"))
            options = q.get("options", {})

            st.markdown(f"### Q{qid}. {q.get('question')}")
            st.caption(
                f"Section: {q.get('section', 'General')} | "
                f"Marks: {q.get('marks', 1)}"
            )

            if options:
                selected = st.radio(
                    "Choose answer",
                    list(options.keys()),
                    format_func=lambda x, opts=options: f"{x}. {opts[x]}",
                    key=f"mock_answer_{qid}",
                )
                user_answers[qid] = selected
            else:
                st.error("This question has no options. Please generate a new mock test.")

            st.markdown("---")

        if st.button("Submit Mock Test"):
            total_score, max_score, results = calculate_score(questions, user_answers)

            wrong_count = len([r for r in results if not r["is_correct"]])
            negative_score = wrong_count * negative_marks if negative_marking else 0
            final_score = max(0, total_score - negative_score)
            percentage = round((final_score / max_score) * 100, 2) if max_score else 0

            result_payload = {
                "username": st.session_state.get("username"),
                "mode": mode,
                "subject": subject,
                "chapter": chapter,
                "mock_type": mock_type,
                "exam_type": exam_type if mock_type == "CBSE Exam Mock Test" else "SOF Olympiad",
                "difficulty": mock_difficulty,
                "score": final_score,
                "raw_score": total_score,
                "max_score": max_score,
                "percentage": percentage,
                "wrong_count": wrong_count,
                "negative_marking": negative_marking,
                "negative_marks": negative_marks,
                "date": datetime.now().isoformat(),
                "results": results,
            }

            st.session_state[results_key] = result_payload
            st.session_state[submitted_key] = True
            save_test_result(result_payload)

        if st.session_state.get(submitted_key) and results_key in st.session_state:
            result_payload = st.session_state[results_key]

            st.success(
                f"🎯 Final Score: {result_payload['score']} / {result_payload['max_score']}"
            )
            st.info(f"Percentage: {result_payload['percentage']}%")

            if result_payload.get("negative_marking"):
                negative_score = result_payload["wrong_count"] * result_payload["negative_marks"]
                st.warning(f"Negative marking applied: -{negative_score}")

            if result_payload["percentage"] >= 85:
                st.success("Recommended next difficulty: Hard / Olympiad HOTS")
            elif result_payload["percentage"] >= 60:
                st.info("Recommended next difficulty: Medium")
            else:
                st.warning("Recommended next difficulty: Easy with revision")

            st.subheader("📘 Detailed Review")

            for result in result_payload["results"]:
                if result["is_correct"]:
                    st.success(f"Q{result['id']}: Correct")
                else:
                    st.error(f"Q{result['id']}: Incorrect")

                options = result.get("options", {})
                selected = result.get("selected")
                correct = result.get("correct")

                selected_text = options.get(selected, "Not answered")
                correct_text = options.get(correct, "")

                st.write(f"Your Answer: **{selected}. {selected_text}**")
                st.write(f"Correct Answer: **{correct}. {correct_text}**")
                st.write(f"Explanation: {result.get('explanation', '')}")
                st.markdown("---")


# =========================================================
# TAB 5 - LEARNING RESOURCES
# =========================================================
with tab5:
    st.subheader("🎥 Additional Learning Resources")

    st.write("""
Explore free videos, tutorials, simulations, and reference material
for deeper understanding.
""")

    chapter_resources = get_resources_for_topic(subject, chapter)

    for resource in chapter_resources:
        show_resource(resource)


# =========================================================
# TAB 6 - ANALYTICS
# =========================================================
with tab6:
    st.subheader("📊 Student Analytics")

    username = st.session_state.get("username")
    history = get_user_history(username)

    if not history:
        st.info("No test history yet. Submit a mock test to see analytics.")
    else:
        total_tests = len(history)
        avg_score = round(sum(item.get("percentage", 0) for item in history) / total_tests, 2)
        best_score = max(item.get("percentage", 0) for item in history)
        latest_score = history[-1].get("percentage", 0)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Tests Taken", total_tests)
        col2.metric("Average Score", f"{avg_score}%")
        col3.metric("Best Score", f"{best_score}%")
        col4.metric("Latest Score", f"{latest_score}%")

        subject_summary = {}
        for item in history:
            s = item.get("subject", "Unknown")
            subject_summary.setdefault(s, {"count": 0, "total": 0})
            subject_summary[s]["count"] += 1
            subject_summary[s]["total"] += item.get("percentage", 0)

        st.subheader("Subject-wise Performance")
        for s, data in subject_summary.items():
            avg = round(data["total"] / data["count"], 2)
            st.write(f"**{s}** — Tests: {data['count']} | Average: {avg}%")

        st.subheader("Recent Test History")
        for item in reversed(history[-10:]):
            st.write(
                f"**{item.get('subject')} - {item.get('chapter')}** | "
                f"{item.get('difficulty')} | "
                f"{item.get('percentage')}% | "
                f"{item.get('date', '')[:10]}"
            )


# =========================================================
# TAB 7 - LEADERBOARD
# =========================================================
with tab7:
    st.subheader("🏆 Leaderboard")

    leaderboard = get_leaderboard()

    if not leaderboard:
        st.info("No leaderboard data yet. Submit mock tests to populate the leaderboard.")
    else:
        for rank, item in enumerate(leaderboard, start=1):
            st.write(
                f"**#{rank} {item['username']}** — "
                f"Average: {item['average_score']}% | "
                f"Best: {item['best_score']}% | "
                f"Tests: {item['tests']}"
            )


# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("© 2026 Grade 9 CBSE + SOF Olympiad AI Tutor, Created by PB for AB")
