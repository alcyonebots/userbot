import asyncio
import logging
from pymongo import MongoClient
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from userbot import start_userbot

# MongoDB setup
client = MongoClient("mongodb+srv://Cenzo:Cenzo123@cenzo.azbk1.mongodb.net/")
db = client["reaper"]
sessions_collection = db["sessions"]

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


async def clone(update: Update, context: CallbackContext):
    """Clone and start a userbot session."""
    try:
        if not context.args or len(context.args) == 0:
            update.message.reply_text("Please provide a valid Pyrogram session string.")
            return

        string_session = context.args[0]
        user_id = update.message.from_user.id

        # Save session string to MongoDB
        sessions_collection.update_one(
            {"user_id": user_id},
            {"$set": {"string_session": string_session}},
            upsert=True,
        )

        update.message.reply_text("Session cloned successfully! Starting your userbot...")

        # Start userbot for this session
        asyncio.create_task(start_userbot(string_session, user_id))

    except Exception as e:
        logger.error(f"Error in /clone command: {e}")
        update.message.reply_text(f"An error occurred: {e}")


def load_sessions():
    """Load all sessions from MongoDB and start userbots."""
    saved_sessions = sessions_collection.find()
    tasks = []
    for session in saved_sessions:
        string_session = session.get("string_session")
        user_id = session.get("user_id")
        if string_session and user_id:
            tasks.append(asyncio.create_task(start_userbot(string_session, user_id)))
    return tasks


def help_command(update: Update, context: CallbackContext):
    """Provide help information."""
    help_text = """Available commands:
    /clone <string_session> - Clone a Pyrogram session and start the userbot
    /help - Show this help message
    """
    update.message.reply_text(help_text)


def main():
    """Start the main Telegram bot."""
    BOT_TOKEN = "7734408721:AAHwWAuqGoAWrDuKSIstabuRHIaJzltQTaw"
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Register commands
    dp.add_handler(CommandHandler("clone", clone))
    dp.add_handler(CommandHandler("help", help_command))

    # Start bot and userbots
    updater.start_polling()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*load_sessions()))
    updater.idle()


if __name__ == "__main__":
    main()
