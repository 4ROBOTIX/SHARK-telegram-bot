import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
LANG_DEFAULT = "cz"

HUMAN_TRIGGER_KEYWORDS = [
    "chci mluvit s člověkem",
    "kontaktuj podporu",
    "přepoj mě na člověka",
    "live support",
    "potřebuji živou pomoc",
    "dej mi kolegu"
]