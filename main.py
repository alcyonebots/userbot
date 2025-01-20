import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from userbot import start_userbot
from db import load_sessions, save_session

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def clone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /clone command")
    try:
        if not context.args or len(context.args) == 0:
            await update.message.reply_text("Please provide a valid Telethon string session.")
            return

        string_session = context.args[0]
        user_id = update.message.from_user.id
        save_session(user_id, string_session)
        await update.message.reply_text("Session cloned successfully! Starting your userbot...")
        asyncio.create_task(start_userbot(string_session, user_id))
    except Exception as e:
        logger.error(f"Error in /clone: {e}")
        await update.message.reply_text(f"An error occurred: {e}")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Received /ping from {update.effective_user.id}")
    await update.message.reply_text("Pong!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /help command")
    help_text = """Available commands:
    /ping - Check latency
    /raid <number of messages> - Start raid with random quotes
    /spam <number of messages> <text> - Spam a custom message
    /stop - Stop any ongoing actions (raid, spam, echo, rraid)
    /echo - Continuously echo the message you reply to
    /rraid - Continuously reply with random quotes when the target user sends a message
    """
    await update.message.reply_text(help_text)

async def main():
    BOT_TOKEN = '7734408721:AAHwWAuqGoAWrDuKSIstabuRHIaJzltQTaw'  # Replace with your bot token

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("clone", clone))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping))

    await application.initialize()
    await application.start()
    logger.info("Bot started. Waiting for commands...")
    await asyncio.Event().wait()
    await application.stop()
    await application.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
