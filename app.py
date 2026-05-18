import streamlit as st
from data.syllabus import CBSE_9, SOF_9
from services.tutor import generate_lesson, answer_doubt
from services.quiz import generate_quiz

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass


st.set_page_config(
    page_title="Grade 9 CBSE AI Tutor",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Grade 9 CBSE + SOF Olympiad AI Tutor")

mode = st.sidebar.radio(
    "Choose Mode",
    ["CBSE Chapter Tutor", "SOF Olympiad Tutor"]
)

if mode == "CBSE Chapter Tutor":
    subject = st.sidebar.selectbox("Subject", list(CBSE_9.keys()))
    chapter = st.sidebar.selectbox("Chapter", CBSE_9[subject])
else:
    subject = st.sidebar.selectbox("Olympiad", list(SOF_9.keys()))
    chapter = st.sidebar.selectbox("Section", SOF_9[subject])

tab1, tab2, tab3 = st.tabs(["Lesson", "Ask Doubt", "Quiz"])

with tab1:
    st.subheader("Methodical Lesson")
    if st.button("Generate Lesson"):
        with st.spinner("Preparing lesson..."):
            lesson = generate_lesson(subject, chapter, mode)
            st.markdown(lesson)

with tab2:
    st.subheader("Ask a Doubt")
    doubt = st.text_area("Type your question")
    if st.button("Explain"):
        if doubt.strip():
            with st.spinner("Thinking..."):
                answer = answer_doubt(subject, chapter, doubt)
                st.markdown(answer)
        else:
            st.warning("Please type a question.")

with tab3:
    st.subheader("Practice Quiz")
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Olympiad HOTS"])
    count = st.slider("Number of questions", 3, 15, 5)

    if st.button("Generate Quiz"):
        with st.spinner("Creating quiz..."):
            quiz = generate_quiz(subject, chapter, mode, difficulty, count)
            st.markdown(quiz)