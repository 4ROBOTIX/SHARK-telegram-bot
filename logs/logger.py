import os
import json
from datetime import datetime
from ftplib import FTP

# Název lokálního souboru (bude se generovat podle roku a měsíce)
def get_log_filename():
    return f"interactions_{datetime.utcnow().strftime('%Y-%m')}.json"

def log_interaction(username, user_input, answer, user_id=None):
    filename = get_log_filename()
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "username": username,
        "user_id": user_id,
        "question": user_input,
        "answer": answer
    }

    # Načti existující logy (nebo začni s prázdným polem)
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Přidej nový záznam
    data.append(log_entry)

    # Ulož lokálně
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Odešli na FTP
    upload_to_ftp(filename)

def upload_to_ftp(filename):
    # PŘIHLAŠOVACÍ ÚDAJE Z ENVIRONMENT VARIABLŮ
    ftp_host = os.environ.get("FTP_HOST")
    ftp_user = os.environ.get("FTP_USER")
    ftp_pass = os.environ.get("FTP_PASS")
    ftp_folder = os.environ.get("FTP_FOLDER", "logs")  # výchozí složka: "logs"

    if not all([ftp_host, ftp_user, ftp_pass]):
        print("⚠️ FTP přihlašovací údaje nejsou kompletní. Přeskočeno nahrávání na FTP.")
        return

    try:
        with FTP(ftp_host) as ftp:
            ftp.login(ftp_user, ftp_pass)

            # Přejdi do cílové složky (vytvoříme, pokud neexistuje)
            try:
                ftp.cwd(ftp_folder)
            except:
                ftp.mkd(ftp_folder)
                ftp.cwd(ftp_folder)

            with open(filename, "rb") as file:
                ftp.storbinary(f"STOR {filename}", file)

            print(f"✅ Soubor {filename} byl úspěšně nahrán na FTP ({ftp_folder}/).")

    except Exception as e:
        print(f"❌ Chyba při nahrávání na FTP: {e}")
