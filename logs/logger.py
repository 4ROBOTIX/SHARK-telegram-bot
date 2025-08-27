import os
from datetime import datetime

def log_unanswered(user, question):
    with open("logs/unanswered.log", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] @{user}: {question}\n")

def log_interaction(user, question, answer):
    with open("logs/interactions.log", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] @{user}: {question} -> {answer}\n")
