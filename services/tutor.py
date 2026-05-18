from services.llm import ask_llm

TUTOR_SYSTEM = """
You are a patient Grade 9 CBSE tutor for an Indian student.
Teach methodically using:
1. Concept overview
2. Simple explanation
3. Example
4. Common mistakes
5. Practice questions
6. Short recap

Use age-appropriate language.
For Hindi, explain in Hindi.
For Olympiad mode, include HOTS and reasoning-based questions.
Do not hallucinate textbook page numbers.
"""

def generate_lesson(subject, chapter, mode):
    prompt = f"""
Create a structured lesson.

Mode: {mode}
Subject: {subject}
Chapter/Topic: {chapter}
Grade: 9 CBSE

Include:
- Learning objectives
- Explanation
- Worked examples
- 5 practice questions
- 2 challenge questions
- Quick revision notes
"""
    return ask_llm(TUTOR_SYSTEM, prompt)

def answer_doubt(subject, chapter, question):
    prompt = f"""
Subject: {subject}
Chapter: {chapter}

Student doubt:
{question}

Explain step by step. Ask one follow-up practice question at the end.
"""
    return ask_llm(TUTOR_SYSTEM, prompt)