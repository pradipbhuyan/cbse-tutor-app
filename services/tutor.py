from services.llm import ask_llm
from services.rag import search_textbook_content

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
    retrieved = search_textbook_content(
        query=step_title,
        subject=subject,
        chapter=chapter,
        top_k=5
    )

    context = "\n\n".join(
        [
            f"Source: {meta['source_name']}, Page: {meta.get('page_number', '')}\n{doc}"
            for doc, meta in retrieved
        ]
    )

    prompt = f"""
Mode: {mode}
Subject: {subject}
Chapter: {chapter}
Current sub-topic: {step_title}

TEXTBOOK CONTEXT:
{context}

Create a focused lesson using the textbook context.
Do not invent textbook lines.
If context is missing, clearly say: "No textbook context found for this topic."
"""

    return ask_llm(TUTOR_SYSTEM, prompt)
