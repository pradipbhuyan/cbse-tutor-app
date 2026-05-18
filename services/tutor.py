from services.llm import ask_llm

TUTOR_SYSTEM = """
You are a patient Grade 9 CBSE tutor.

Teach only the requested sub-topic.
Do not give the full chapter at once.

Use this structure:
1. What you will learn
2. Simple explanation
3. Step-by-step breakdown
4. Worked example
5. Common mistake
6. Quick check question
7. Summary

Use simple language for a 14-15 year old student.
For Olympiad mode, include reasoning and HOTS thinking.
For Hindi, explain in Hindi.
"""


def generate_step_lesson(subject, chapter, mode, step_title, teacher_persona=""):
    prompt = f"""
Mode: {mode}
Subject: {subject}
Chapter: {chapter}
Current sub-topic: {step_title}

Teacher Persona:
{teacher_persona}

Create a focused step-wise lesson only for this sub-topic.
Do not cover unrelated topics.
End with one small question to check understanding.
"""
    return ask_llm(TUTOR_SYSTEM, prompt)


def answer_doubt(subject, chapter, question):
    prompt = f"""
Subject: {subject}
Chapter: {chapter}

Student doubt:
{question}

Explain step by step.
"""
    return ask_llm(TUTOR_SYSTEM, prompt)
