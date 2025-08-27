import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from knowledge.qa import get_answer
from logs.logger import log_unanswered, log_interaction

# Nastavení logování
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Získání tokenu a webhook URL
BOT_TOKEN = os.environ["BOT_TOKEN"]
RENDER_EXTERNAL_URL = os.environ["RENDER_EXTERNAL_URL"]

# Vytvoření aplikace
application = Application.builder().token(BOT_TOKEN).build()

# Základní příkaz /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ahoj! Jsem SHARK support bot. Zeptej se mě na cokoliv ohledně SHARK EA.")

# Zpracování běžných zpráv
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    user_id = update.message.from_user.id

    answer = get_answer(user_question)

    if answer:
        await update.message.reply_text(answer)
        log_interaction(user_id, user_question, answer)
    else:
        await update.message.reply_text("Promiň, na tohle zatím neznám odpověď. Přepošlu to týmu.")
        log_unanswered(user_id, user_question)

# Registrace handlerů
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook mód pro Render
application.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 8443)),
    webhook_secret_path = os.environ.get("WEBHOOK_SECRET_PATH", "shark-secret")
    webhook_url = f"https://{RENDER_EXTERNAL_URL}/webhook/{webhook_secret_path}"
)
