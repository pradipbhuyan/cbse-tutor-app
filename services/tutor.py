from services.llm import ask_llm
#from services.rag import search_textbook_content

TUTOR_SYSTEM = """
You are a Grade 9 CBSE tutor.

Use the provided textbook context first.
If context is insufficient, say so and then explain using general knowledge.

Teach step-by-step:
1. What you will learn
2. Textbook-based explanation
3. Simple explanation
4. Worked example
5. Common mistakes
6. Practice question
7. Summary
"""


def generate_step_lesson(subject, chapter, mode, step_title):
    prompt = f"""
Mode: {mode}
Subject: {subject}
Chapter: {chapter}
Current sub-topic: {step_title}

Create a focused step-wise lesson only for this sub-topic.
Do not cover unrelated topics.

Teach using:
1. What you will learn
2. Simple explanation
3. Step-by-step breakdown
4. Worked example
5. Common mistake
6. Quick check question
7. Summary
"""
    return ask_llm(TUTOR_SYSTEM, prompt)
