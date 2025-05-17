from openai import OpenAI
import os
import json
import random
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_question(round_type, session):
    with open(f'interview_data/questions_{round_type}.json', 'r') as file:
        questions = json.load(file)

    # Get asked list from session
    asked_key = f"asked_{round_type}"
    asked = session.get(asked_key, [])

    # Filter out already asked
    remaining = [q for q in questions if q not in asked]
    if not remaining:
        remaining = questions  # Reset if all used

    question = random.choice(remaining)
    asked.append(question)
    session[asked_key] = asked

    return question


def evaluate_answer(question, answer):
    prompt = f"""
You are an interview evaluator. A candidate was asked:

Question: {question}
Answer: {answer}

Give concise feedback and a score out of 10 (only integer). 

Respond in JSON format like:
{{"feedback": "Your feedback here", "score": 6}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse the JSON response safely
    import json
    text = response.choices[0].message.content.strip()

    try:
        result = json.loads(text)
        feedback = result.get("feedback", "No feedback given.")
        score = int(result.get("score", 0))
    except Exception as e:
        feedback = "Could not parse evaluation."
        score = 0

    return feedback, score
