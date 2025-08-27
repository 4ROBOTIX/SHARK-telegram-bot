import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters
from config import TELEGRAM_BOT_TOKEN, LANG_DEFAULT, HUMAN_TRIGGER_KEYWORDS
from knowledge.qa import get_answer
from logs.logger import log_unanswered, log_interaction

user_flags = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ahoj! 🤖 Jsem SHARK Support Bot. Ptej se mě na cokoliv ohledně nastavení nebo funkcí.")

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Zatím umím jen česky 🇨🇿. Angličtina je v přípravě.")

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_flags[update.effective_user.id] = False
    await update.message.reply_text("Pokračujeme! Jsem zpět.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text

    if any(k.lower() in message.lower() for k in HUMAN_TRIGGER_KEYWORDS):
        user_flags[user_id] = True
        await update.message.reply_text("Rozumím. Předávám tě kolegovi. Ozve se ti co nejdřív.")
        print(f"[PŘEPOJENO] Uživatel @{update.effective_user.username} požaduje ruční pomoc: {message}")
        return

    if user_flags.get(user_id):
        await update.message.reply_text("Prosím vyčkej na kolegu...")
        return

    answer = get_answer(message)
    if answer:
        await update.message.reply_text(answer)
    else:
        await update.message.reply_text("Tuhle odpověď zatím neznám. Předávám si ji dál k doplnění.")
        log_unanswered(update.effective_user.username, message)
    log_interaction(update.effective_user.username, message, answer or "Neznámá otázka")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("language", language))
    app.add_handler(CommandHandler("resume", resume))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()