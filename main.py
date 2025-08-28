print("==== SPUŠTĚNA VERZE TEST 16 ====")

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
from logs.logger import log_interaction, log_unanswered
from telegram.request import HTTPXRequest
from telegram.error import TelegramError

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_SECRET_PATH = os.environ["WEBHOOK_SECRET_PATH"]

logging.basicConfig(level=logging.INFO)

# === Vytvoření telegramové aplikace ===
request = HTTPXRequest(pool_limits=10)  # 10 současných spojení místo výchozích 100ms timeoutů
app = Application.builder().token(BOT_TOKEN).request(request).build()

# === Telegram Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ahoj, jsem Rafael, 4ROBOTIX asistent. Jak mohu pomoci?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    answer = get_answer(user_input)

    log_interaction(update.message.from_user.username, user_input, answer)

    if answer:
        await update.message.reply_text(answer)
    else:
        await update.message.reply_text("Omlouvám se, na to zatím neznám odpověď.")
        log_unanswered(update.message.from_user.username, user_input)

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

@flask_app.route(f"/webhook/{WEBHOOK_SECRET_PATH}", methods=["POST"])
async def webhook():
    global is_initialized
    if not is_initialized:
        await app.initialize()  # 🔧 nutné pro webhook
        is_initialized = True

    data = request.get_json(force=True)
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return "OK"

# === Spuštění Flask serveru ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)
