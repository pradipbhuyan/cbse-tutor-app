import streamlit as st
from data.syllabus import CBSE_9, SOF_9
from services.tutor import generate_lesson, answer_doubt
from services.quiz import generate_quiz

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

    st.subheader("📖 AI Generated Lesson")

    st.write(f"### Subject: {subject}")
    st.write(f"### Topic: {chapter}")

    if st.button("Generate Lesson"):

        with st.spinner("Generating lesson..."):

            lesson = generate_lesson(
                subject,
                chapter,
                mode
            )

            st.markdown(lesson)


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
