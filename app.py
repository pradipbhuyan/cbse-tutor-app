import streamlit as st

from services.tutor import generate_step_lesson, answer_doubt
from services.progress import get_current_step, save_current_step, mark_completed
from data.syllabus import CBSE_9, SOF_9, LESSON_STEPS

from services.llm import generate_speech

# -----------------------------
# Streamlit Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Grade 9 CBSE AI Tutor",
    page_icon="📚",
    layout="wide"
)

# -----------------------------
# Dummy Users for Login
# -----------------------------
USERS = {
    "parent": "parent123",
    "student": "student123"
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
# Logout
# -----------------------------
def logout_button():

    with st.sidebar:

        st.write(f"👤 Logged in as: **{st.session_state.get('username')}**")

        if st.button("Logout"):

            st.session_state["logged_in"] = False
            st.session_state["username"] = None

            st.rerun()


# -----------------------------
# Session State Initialization
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "username" not in st.session_state:
    st.session_state["username"] = None


# -----------------------------
# Show Login Page if not logged in
# -----------------------------
if not st.session_state["logged_in"]:
    login_page()
    st.stop()


# -----------------------------
# Sidebar Logout
# -----------------------------
logout_button()


# -----------------------------
# Main Application
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
# Sidebar Options
# -----------------------------
mode = st.sidebar.radio(
    "Choose Learning Mode",
    ["CBSE Chapter Tutor", "SOF Olympiad Tutor"]
)

# -----------------------------
# Subject & Chapter Selection
# -----------------------------
if mode == "CBSE Chapter Tutor":

    subject = st.sidebar.selectbox(
        "Select Subject",
        list(CBSE_9.keys())
    )

    chapter = st.sidebar.selectbox(
        "Select Chapter",
        CBSE_9[subject]
    )

else:

    subject = st.sidebar.selectbox(
        "Select Olympiad",
        list(SOF_9.keys())
    )

    chapter = st.sidebar.selectbox(
        "Select Section",
        SOF_9[subject]
    )


# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3 = st.tabs([
    "📖 Lesson",
    "❓ Ask Doubt",
    "📝 Quiz"
])



# =========================================================
# TAB 1 - LESSON GENERATOR
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

    if "lesson_step" not in st.session_state:
        st.session_state["lesson_step"] = saved_step

    current_step = st.session_state["lesson_step"]

    st.progress((current_step + 1) / len(steps))

    st.write(f"### Subject: {subject}")
    st.write(f"### Chapter/Topic: {chapter}")
    st.write(f"### Step {current_step + 1} of {len(steps)}")
    st.info(f"Current Learning Step: **{steps[current_step]}**")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⬅ Previous") and current_step > 0:
            st.session_state["lesson_step"] -= 1
            save_current_step(username, mode, subject, chapter, st.session_state["lesson_step"])
            st.rerun()

    with col2:
        if st.button("✅ Mark Step Complete"):
            if current_step < len(steps) - 1:
                st.session_state["lesson_step"] += 1
                save_current_step(username, mode, subject, chapter, st.session_state["lesson_step"])
                st.rerun()
            else:
                mark_completed(username, mode, subject, chapter)
                st.success("Chapter completed!")

    with col3:
        if st.button("🔄 Restart Chapter"):
            st.session_state["lesson_step"] = 0
            save_current_step(username, mode, subject, chapter, 0)
            st.rerun()

    if st.button("Generate This Step Lesson"):

        with st.spinner("Generating focused lesson..."):

            lesson = generate_step_lesson(
                subject,
                chapter,
                mode,
                steps[current_step]
            )
            
            st.session_state["current_lesson"] = lesson
            
            st.markdown(lesson)
            
            if st.button("🔊 Read Aloud"):
            
                with st.spinner("Generating audio..."):
            
                    audio_file = generate_speech(lesson)
            
                    audio_bytes = open(audio_file, "rb").read()
            
                    st.audio(audio_bytes, format="audio/mp3")


# =========================================================
# TAB 2 - ASK DOUBT
# =========================================================
with tab2:

    st.subheader("❓ Ask Your Doubt")

    doubt = st.text_area(
        "Type your question here"
    )

    if st.button("Explain Doubt"):

        if doubt.strip() == "":
            st.warning("Please enter a question.")

        else:

            with st.spinner("Thinking..."):

                answer = answer_doubt(
                    subject,
                    chapter,
                    doubt
                )

                st.markdown(answer)


# =========================================================
# TAB 3 - QUIZ
# =========================================================
with tab3:

    st.subheader("📝 Practice Quiz")

    difficulty = st.selectbox(
        "Select Difficulty",
        [
            "Easy",
            "Medium",
            "Hard",
            "Olympiad HOTS"
        ]
    )

    count = st.slider(
        "Number of Questions",
        3,
        15,
        5
    )

    if st.button("Generate Quiz"):

        with st.spinner("Creating quiz..."):

            quiz = generate_quiz(
                subject,
                chapter,
                mode,
                difficulty,
                count
            )

            st.markdown(quiz)


# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("© 2026 Grade 9 CBSE + SOF Olympiad AI Tutor")
