print("==== SPUŠTĚNA VERZE TEST 9 ====")

import os
import nest_asyncio
nest_asyncio.apply()

from telegram import Update
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from knowledge.qa import get_answer
from logs.logger import log_interaction, log_unanswered

import logging
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["BOT_TOKEN"]
RENDER_EXTERNAL_URL = os.environ["RENDER_EXTERNAL_URL"]
WEBHOOK_SECRET_PATH = os.environ["WEBHOOK_SECRET_PATH"]

# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ahoj, jsem Rafael, 4ROBOTIX asistent. Jak mohu pomoci?.")

async def main():
    print("Startuji aplikaci...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Přidání handlerů
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # 🔧 TESTOVACÍ HANDLER PRO WEBHOOK
    async def test_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE):
        print("Zachycen testovací zpráva přes webhook.")
        await update.message.reply_text("Webhook funguje!")

    app.add_handler(CommandHandler("test", test_webhook))

    # 🔔 LOG WEBHOOK URL
    print(f"Webhook URL: {RENDER_EXTERNAL_URL}/webhook/{WEBHOOK_SECRET_PATH}")

    # 🌐 Spuštění webhooku
    print("Spouštím run_webhook()...")
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"{RENDER_EXTERNAL_URL}/webhook/{WEBHOOK_SECRET_PATH}",
        secret_token=WEBHOOK_SECRET_PATH
    )

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
    print(f"Webhook URL: {RENDER_EXTERNAL_URL}/webhook/{WEBHOOK_SECRET_PATH}")
    
    import asyncio
    asyncio.get_event_loop().run_until_complete(main())
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Spouštím run_webhook()...")
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"{RENDER_EXTERNAL_URL}/webhook/{WEBHOOK_SECRET_PATH}",
    )
