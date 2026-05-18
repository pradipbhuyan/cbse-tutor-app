import json
from services.llm import ask_llm

MOCK_TEST_SYSTEM = """
You create original Grade 9 SOF Science Olympiad style mock tests.
Do not copy previous year questions verbatim.
Create questions inspired by common SOF NSO/ISO patterns: logical reasoning, science concepts, application, data interpretation, assertion-reason, and achievers/HOTS.
Return ONLY valid JSON. No markdown.

JSON schema:
{
  "questions": [
    {
      "id": 1,
      "section": "Logical Reasoning|Science|Achievers Section",
      "question": "...",
      "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
      "answer": "A",
      "explanation": "...",
      "marks": 1
    }
  ]
}
"""


def generate_science_olympiad_mock_test(num_questions=10, difficulty="Medium"):
    prompt = f"""
Create a Class 9 SOF Science Olympiad style mock test.
Difficulty: {difficulty}
Number of questions: {num_questions}

Pattern:
- Logical Reasoning: about 20%
- Science: about 70%
- Achievers Section/HOTS: about 10%

Use Class 9 CBSE/NCERT science plus previous-class foundational concepts where useful.
Include Physics, Chemistry, Biology, and reasoning.

Return only valid JSON.
"""

    raw = ask_llm(MOCK_TEST_SYSTEM, prompt)

    try:
        data = json.loads(raw)
        return data.get("questions", [])
    except Exception:
        return []


def calculate_score(questions, user_answers):
    total_score = 0
    max_score = 0
    results = []

    for q in questions:
        qid = str(q.get("id"))
        correct = q.get("answer")
        selected = user_answers.get(qid)
        marks = int(q.get("marks", 1))
        max_score += marks

        is_correct = selected == correct
        if is_correct:
            total_score += marks

        results.append({
            "id": q.get("id"),
            "section": q.get("section"),
            "question": q.get("question"),
            "selected": selected,
            "correct": correct,
            "is_correct": is_correct,
            "marks": marks,
            "options": q.get("options", {}),
            "explanation": q.get("explanation", "")
        })

    return total_score, max_score, results
