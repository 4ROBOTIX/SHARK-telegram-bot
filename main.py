print("==== SPUŠTĚNA VERZE TEST 14 ====")

import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from knowledge.qa import get_answer
from logs.logger import log_interaction, log_unanswered

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_SECRET_PATH = os.environ["WEBHOOK_SECRET_PATH"]

logging.basicConfig(level=logging.INFO)

app = Application.builder().token(BOT_TOKEN).build()

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

# Přidání handlerů
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("test", test_webhook))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === Flask server ===
flask_app = Flask(__name__)

@flask_app.route(f"/webhook/{WEBHOOK_SECRET_PATH}", methods=["POST"])
async def webhook():
    if request.method == "POST":
        data = request.get_json(force=True)
        update = Update.de_json(data, app.bot)
        await app.process_update(update)
        return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)
