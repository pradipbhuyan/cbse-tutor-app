from services.llm import ask_llm

QUIZ_SYSTEM = """
You generate Grade 9 CBSE and SOF Olympiad quizzes.
Return questions with options, answer key, and explanation.
Keep difficulty appropriate to the selected mode.
"""

def generate_quiz(subject, chapter, mode, difficulty, count):
    prompt = f"""
Generate {count} MCQs.

Subject: {subject}
Chapter/Topic: {chapter}
Mode: {mode}
Difficulty: {difficulty}

Return in this format:
Q1.
A.
B.
C.
D.
Answer:
Explanation:
"""
    return ask_llm(QUIZ_SYSTEM, prompt)