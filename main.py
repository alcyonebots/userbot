from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "7734408721:AAHwWAuqGoAWrDuKSIstabuRHIaJzltQTaw"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /start or /help to test.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Adding command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Start the bot
    print("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
