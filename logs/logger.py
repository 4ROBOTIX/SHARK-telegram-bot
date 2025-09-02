import os
import json
from datetime import datetime
from ftplib import FTP

FTP_HOST = os.environ.get("FTP_HOST", "x")
FTP_USER = os.environ.get("FTP_USER", "x")
FTP_PASS = os.environ.get("FTP_PASS", "x")
FTP_FOLDER = os.environ.get("FTP_FOLDER", "")  # např. "logs"

def log_interaction(username, user_input, answer, user_id=None, answered_by="bot"):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "username": username,
        "user_id": user_id,
        "question": user_input,
        "answer": answer,
        "answered_by": answered_by  # nově přidáno
    }

    file_name = f"interactions_{datetime.utcnow().strftime('%Y-%m')}.json"
    local_path = file_name

    # Načíst existující záznamy
    if os.path.exists(local_path):
        with open(local_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(log_entry)

    # Uložit lokálně
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Nahrát na FTP
    try:
        with FTP(FTP_HOST) as ftp:
            ftp.login(FTP_USER, FTP_PASS)
            if FTP_FOLDER:
                ftp.cwd(FTP_FOLDER)
            with open(local_path, "rb") as file:
                ftp.storbinary(f"STOR {file_name}", file)
    except Exception as e:
        print("Chyba při nahrávání na FTP:", e)
