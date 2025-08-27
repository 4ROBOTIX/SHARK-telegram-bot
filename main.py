import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from knowledge.qa import get_answer
from logs.logger import log_interaction, log_unanswered

# Logging
logging.basicConfig(level=logging.INFO)

# Načtení proměnných
BOT_TOKEN = os.environ["BOT_TOKEN"]
RENDER_EXTERNAL_URL = os.environ["RENDER_EXTERNAL_URL"]  # např. shark-telegram-bot.onrender.com
WEBHOOK_SECRET_PATH = os.environ["WEBHOOK_SECRET_PATH"]  # např. shark-secret

# Funkce pro příkaz /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ahoj! Jsem SHARK EA asistent. Zeptej se mě na cokoliv ohledně systému.")

# Funkce pro zpracování zpráv
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.effective_chat.id
    logging.info(f"Zpráva od {chat_id}: {user_message}")

    answer = get_answer(user_message)

    if answer:
        await update.message.reply_text(answer)
        log_interaction(chat_id, user_message, answer)
    else:
        await update.message.reply_text("Omlouvám se, na tohle zatím nemám odpověď.")
        log_unanswered(chat_id, user_message)

# Inicializace aplikace
application = ApplicationBuilder().token(BOT_TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Spuštění bota přes webhook
print(f"Webhook URL: {RENDER_EXTERNAL_URL}/webhook/{WEBHOOK_SECRET_PATH}")
application.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 8443)),
    webhook_url=f"{RENDER_EXTERNAL_URL}/webhook/{WEBHOOK_SECRET_PATH}"
)
