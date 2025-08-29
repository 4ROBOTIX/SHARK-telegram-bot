import os
import json
from datetime import datetime

# Uložení do root složky projektu (funguje i bez placeného disku)
LOG_FILE = "interactions.json"

def log_interaction(username, user_input, answer, user_id=None):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "username": username,
        "user_id": user_id,
        "question": user_input,
        "answer": answer
    }

    # Načti existující logy (pokud soubor existuje)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Přidej nový záznam
    data.append(log_entry)

    # Ulož zpět do souboru
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def log_unanswered(username, user_input, user_id=None):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "username": username,
        "user_id": user_id,
        "question": user_input,
        "answer": None
    }

    UNANSWERED_FILE = "unanswered.json"

    # Načti existující logy
    if os.path.exists(UNANSWERED_FILE):
        with open(UNANSWERED_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(log_entry)

    with open(UNANSWERED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
