import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
import pymongo
import asyncio

# MongoDB setup for storing sessions
client = pymongo.MongoClient("mongodb+srv://Cenzo:Cenzo123@cenzo.azbk1.mongodb.net/")
db = client["reaper"]
sessions_collection = db["sessions"]

# Initialize logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler."""
    await update.message.reply_text("Welcome! Use /help to see available commands.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler."""
    help_text = """Available commands:
    /clone <session> - Clone a Telethon session
    /ping - Check latency
    """
    await update.message.reply_text(help_text)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ping command to check bot latency."""
    latency = context.application.updater.request.read_timeout
    await update.message.reply_text(f"Pong! Latency: {latency * 1000:.2f} ms")

async def clone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clone session command handler."""
    if not context.args or len(context.args) == 0:
        await update.message.reply_text("Please provide a valid session string.")
        return

    string_session = context.args[0]
    user_id = update.effective_user.id

    # Save session to MongoDB
    sessions_collection.update_one(
        {"user_id": user_id},
        {"$set": {"string_session": string_session}},
        upsert=True,
    )
    await update.message.reply_text("Session cloned successfully!")

    # Start the userbot for this session
    from userbot import start_userbot

    asyncio.create_task(start_userbot(string_session, user_id))

# Main function to start the bot
def main():
    BOT_TOKEN = "7734408721:AAHwWAuqGoAWrDuKSIstabuRHIaJzltQTaw"

    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("clone", clone))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
