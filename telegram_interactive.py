import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from league_tools import League, get_last_week_number
from alerts import weekly_alerts

from dotenv import load_dotenv


load_dotenv()  # carrega variáveis do .env


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SLEEPER_LEAGUE_ID = os.getenv("SLEEPER_LEAGUE_ID")


WELCOME_MESSAGE = (
    "👋 Hello, welcome to the Fantasy Football Bot!\n\n"
    "🇧🇷 Olá, bem-vindo ao Bot de Fantasy Football!\n\n"
    "Available commands / Comandos disponíveis:\n"
    "- 'standings' / 'classificação' → Current league standings\n"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if any(word in text for word in ["standings", "classificação", "classificacao"]):
        league = League(SLEEPER_LEAGUE_ID)
        last_week = get_last_week_number(league)  # fallback para semana 1
        alerts_list = weekly_alerts(league, last_week)
        if alerts_list:
            for alert in alerts_list:
                await update.message.reply_text(alert["message"], parse_mode="Markdown")
        else:
            await update.message.reply_text("No standings available at the moment.")
    else:
        await update.message.reply_text(WELCOME_MESSAGE)


def run_bot():

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Telegram interactive bot is running...")
    app.run_polling()

run_bot()