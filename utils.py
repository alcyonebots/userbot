import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from db import sessions_collection
from userbot import start_userbot

async def load_sessions():
    """Load all sessions from MongoDB and start userbots."""
    try:
        saved_sessions = sessions_collection.find()  # Fetch all saved sessions
        tasks = []
        for session in saved_sessions:
            string_session = session.get("string_session")
            user_id = session.get("user_id")
            if string_session:
                # Start a new task for each userbot
                tasks.append(start_userbot(string_session, user_id))
        
        # Run all tasks concurrently
        await asyncio.gather(*tasks)
    except Exception as e:
        print(f"Error loading sessions: {e}")

async def clone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clone and save a user's string session."""
    try:
        if not context.args or len(context.args) == 0:
            await update.message.reply_text("Please provide a valid Pyrogram string session.")
            return

        string_session = context.args[0]

        # Save the session string in MongoDB
        user_id = update.message.from_user.id
        sessions_collection.update_one(
            {"user_id": user_id},
            {"$set": {"string_session": string_session}},
            upsert=True
        )

        await update.message.reply_text("Session cloned successfully! Starting your userbot...")

        # Start the userbot for this session
        asyncio.create_task(start_userbot(string_session, user_id))
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display help text."""
    help_text = """Available commands:
    /ping - Check latency
    /clone <string session> - Clone a Pyrogram string session
    /help - Show this help message
    """
    await update.message.reply_text(help_text)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Respond with latency."""
    await update.message.reply_text("Pong!")
