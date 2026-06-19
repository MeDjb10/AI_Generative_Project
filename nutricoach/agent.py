# agent.py — STEP D: the decision-maker (orchestration + reasoning)
#
# This is what makes the project an AGENT, not just a chatbot:
#   1) decide()  -> one LLM call that READS the question and returns a JSON
#                   decision: which route + why (+ any extracted arguments)
#   2) run()     -> ORCHESTRATION: reads that decision and runs the matching tool
#   3) _phrase() -> turns raw tool output (a dict) into a friendly answer
#
# The flow:  question -> decide -> route to (rag | calculator | food_lookup | direct) -> answer

import os
import sys
import json

# Windows terminals default to cp1252 and crash on emoji (🧠, ➡️). Force UTF-8.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from groq import Groq

# Reuse the pieces you already built and tested:
from rag import answer_with_rag
from tools import calculate_nutrition_needs, food_lookup

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

# This prompt is the "brain". It tells the LLM to act as a router and reply with
# ONLY a JSON object — no prose — so our code can parse the decision reliably.
DECISION_PROMPT = """You are the routing brain of a nutrition assistant.
Read the user's question and choose ONE action:

- "rag": general nutrition/health knowledge questions (diets, foods for a condition, advice).
- "calculator": the user gives body numbers (weight, height, age) and wants BMI or calorie needs.
- "food_lookup": the user asks for nutrition facts of a specific food (calories/protein/etc).
- "direct": small talk or anything the others don't fit.

For "calculator" also extract: weight_kg, height_cm, age, sex (male/female), activity (sedentary/light/moderate/active/very_active).
For "food_lookup" also extract: food_name.

Reply with ONLY valid JSON, no extra text. Examples:
{"action":"rag","reasoning":"..."}
{"action":"calculator","reasoning":"...","weight_kg":75,"height_cm":178,"age":22,"sex":"male","activity":"moderate"}
{"action":"food_lookup","reasoning":"...","food_name":"banana"}

User question: """


def decide(question):
    """Ask the LLM to classify the question and return a parsed decision dict."""
    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": DECISION_PROMPT + question}],
    )
    raw = response.choices[0].message.content.strip()

    # Be defensive: LLMs sometimes wrap JSON in prose or ```code fences```.
    # Grab the substring from the first "{" to the last "}".
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        return json.loads(raw[start:end])
    except Exception:
        # If parsing fails, fall back to RAG (the safest general-purpose route).
        return {"action": "rag",
                "reasoning": "Could not parse decision, defaulting to RAG."}


def run(question, decision=None):
    """Orchestration: decide, show reasoning, run the chosen route, return answer.

    Pass a pre-computed `decision` to reuse one decision (e.g. the web UI shows
    the reasoning first, then reuses the same decision to run the route).
    """
    if decision is None:
        decision = decide(question)
    action = decision.get("action", "rag")

    # Printing the reasoning is the "explain its decisions" requirement.
    print(f"\n🧠 Agent reasoning: {decision.get('reasoning', '(none)')}")
    print(f"➡️  Chosen action: {action}\n")

    if action == "calculator":
        result = calculate_nutrition_needs(
            decision.get("weight_kg"), decision.get("height_cm"),
            decision.get("age"), decision.get("sex", "male"),
            decision.get("activity", "moderate"),
        )
        return _phrase(question, result)

    if action == "food_lookup":
        result = food_lookup(decision.get("food_name", question))
        return _phrase(question, result)

    if action == "direct":
        resp = groq_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": question}],
        )
        return resp.choices[0].message.content

    # default: RAG (uses your vector DB + documents)
    return answer_with_rag(question)


def _phrase(question, tool_result):
    """Let the LLM turn a raw tool dict into a clear, friendly answer."""
    prompt = f"""The user asked: "{question}"
A tool returned this data: {tool_result}
Write a clear, friendly answer based on this data.
Add a short reminder that this is general info, not medical advice."""
    resp = groq_client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": prompt}])
    return resp.choices[0].message.content


if __name__ == "__main__":
    # Test all three tool routes so you can SEE the agent choose correctly.
    tests = [
        "What foods help reduce high blood pressure?",                          # -> rag
        "I'm 68 kg, 170 cm, 25, female, lightly active — my daily calories?",   # -> calculator
        "How much protein is in 100 g of lentils?",                            # -> food_lookup
    ]
    for q in tests:
        print("=" * 70)
        print(f"QUESTION: {q}")
        print(run(q))
        print()
