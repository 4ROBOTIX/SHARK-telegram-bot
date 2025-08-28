import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from knowledge.qa import get_answer
from logs.logger import log_interaction, log_unanswered

BOT_TOKEN = os.environ["BOT_TOKEN"]
RENDER_EXTERNAL_URL = os.environ["RENDER_EXTERNAL_URL"]
WEBHOOK_SECRET_PATH = os.environ["WEBHOOK_SECRET_PATH"]

# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ahoj! Jsem Rafael, 4ROBOTIX asistent. Jak mohu pomoci?.")

# běžné zprávy
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    answer = get_answer(user_input)

    log_interaction(update.message.from_user.username, user_input, answer)

    if answer:
        await update.message.reply_text(answer)
    else:
        await update.message.reply_text("Omlouvám se, na to zatím neznám odpověď.")
        log_unanswered(update.message.from_user.username, user_input)

# hlavní část (není async!)
if __name__ == "__main__":
    print(f"Webhook URL test 3: {RENDER_EXTERNAL_URL}/webhook/{WEBHOOK_SECRET_PATH}")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"{RENDER_EXTERNAL_URL}/webhook/{WEBHOOK_SECRET_PATH}",
    )
