# app.py — STEP E: talk to NutriCoach in the terminal
#
# This is just a loop: read a line from the user -> run() the agent -> print answer.
# All the real work lives in agent.py; this file is only the chat interface.

import sys

# Windows terminals default to cp1252 and crash on emoji (🥗). Force UTF-8.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from agent import run

print("🥗 NutriCoach — ask me about nutrition & health. Type 'quit' to exit.\n")

while True:
    question = input("You: ")
    if question.lower() in ("quit", "exit"):
        print("Goodbye! 👋")
        break
    answer = run(question)        # agent decides the route, runs it, returns text
    print(f"\nNutriCoach: {answer}\n")
