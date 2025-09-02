print("==== SPUŠTĚNA VERZE TEST 20 ====")

import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from knowledge.qa import get_answer
from logs.logger import log_interaction
from telegram.request import HTTPXRequest
from telegram.error import TelegramError

# === ZAČÁTEK UPDATU ===
# ID operátora (Jaro)
OPERATOR_ID = 890406338
active_sessions = set()  # sem se ukládají ID uživatelů, kteří jsou přepojeni

# Fráze pro ruční přepojení
TRANSFER_KEYWORDS = [
    "chci mluvit s člověkem",
    "chci přepojit na člověka",
    "chci přepojit na operátora"
]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.full_name
    message = update.message.text.strip()

    # 1. Pokud operátor napíše "/leave", ukonči přepojení
    if user_id == OPERATOR_ID and message.lower() == "/leave":
        if active_sessions:
            ended_users = ", ".join(str(uid) for uid in active_sessions)
            active_sessions.clear()
            await update.message.reply_text("✅ Konverzace ukončena. Bot opět odpovídá.")
            return
        else:
            await update.message.reply_text("❌ Žádná aktivní konverzace.")
            return

    # 2. Pokud odpovídá operátor (na někoho přepojeného)
    if user_id == OPERATOR_ID and context.chat_data.get("transferred_to"):
        target_id = context.chat_data["transferred_to"]
        await context.bot.send_message(chat_id=target_id, text=message)
        log_interaction("OPERATOR", f"{username} → {target_id}: {message}", "odesláno operátorem", user_id)
        return

    # 3. Pokud je uživatel přepojen na operátora
    if user_id in active_sessions:
        await context.bot.send_message(chat_id=OPERATOR_ID, text=f"{username} ({user_id}): {message}")
        context.chat_data["transferred_to"] = user_id
        log_interaction(username, message, "přesměrováno na operátora", user_id)
        return

    # 4. Klíčová slova pro ruční přepojení
    if message.lower() in TRANSFER_KEYWORDS:
        active_sessions.add(user_id)
        await update.message.reply_text("Spojuji Tě s operátorem. Chvíli strpení...")
        await context.bot.send_message(chat_id=OPERATOR_ID, text=f"🚪 {username} ({user_id}) žádá přepojení na člověka.")
        log_interaction(username, message, "žádost o přepojení", user_id)
        return

    # 5. Standardní zpracování dotazu
    odpoved = get_answer(message)

    if odpoved:
        await update.message.reply_text(odpoved)
        log_interaction(username, message, odpoved, user_id)
    else:
        active_sessions.add(user_id)
        await update.message.reply_text("Prosím o strpení, hledám odpověď, ozvu se co nejdříve.")
        await context.bot.send_message(chat_id=OPERATOR_ID, text=f"🚨 {username} ({user_id}) položil dotaz, na který neznám odpověď: '{message}'")
        log_interaction(username, message, "Odpověď neznáma - přepojuji", user_id)
        context.chat_data["transferred_to"] = user_id

# a pak klasicky handler:

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
# === KONEC UPDATU ===



BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_SECRET_PATH = os.environ["WEBHOOK_SECRET_PATH"]

logging.basicConfig(level=logging.INFO)

# === Vytvoření telegramové aplikace ===
telegram_request = HTTPXRequest(http_version="1.1")  # ✅ Jiný název proměnné
app = Application.builder().token(BOT_TOKEN).request(telegram_request).build()

# === Telegram Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ahoj, jsem Rafael, 4ROBOTIX asistent. Jak mohu pomoci?")

async def test_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Zachycen testovací zpráva přes webhook.")
    await update.message.reply_text("Webhook funguje!")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(f"Exception while handling update {update}: {context.error}")

app.add_error_handler(error_handler)

# Přidání handlerů
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("test", test_webhook))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === Flask server ===
flask_app = Flask(__name__)

# === Zajištění inicializace Application ===
is_initialized = False

# Globální loop
loop = asyncio.get_event_loop()

@flask_app.route(f"/webhook/{WEBHOOK_SECRET_PATH}", methods=["POST"])
def webhook():
    if request.method == "POST":
        print("📩 Přišla zpráva přes webhook")
        data = request.get_json(force=True)
        update = Update.de_json(data, app.bot)

        print(f"📨 Zpráva od: {update.effective_user.username} - {update.effective_message.text}")
        
        # Spuštění async úlohy bezpečně v hlavní asyncio smyčce
        asyncio.run_coroutine_threadsafe(app.process_update(update), loop)

        return "OK"

# === Spuštění Flask serveru ===
if __name__ == "__main__":
    # Inicializace telegram aplikace (nutná pro process_update)
    loop.run_until_complete(app.initialize())
    
    import threading

    # Spusť asyncio loop ve vlákně
    def run_loop():
        print("✅ Asyncio event loop běží...")
        loop.run_forever()

    threading.Thread(target=run_loop).start()

    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)
