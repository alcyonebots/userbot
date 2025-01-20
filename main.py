import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from userbot import start_userbot
from db import load_sessions, save_session

# Clone command for the bot
async def clone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args or len(context.args) == 0:
            await update.message.reply_text("Please provide a valid Telethon string session.")
            return

        string_session = context.args[0]

        # Save the session string in MongoDB for the user
        user_id = update.message.from_user.id
        save_session(user_id, string_session)

        await update.message.reply_text("Session cloned successfully! Starting your userbot...")

        # Start the userbot for this session
        asyncio.create_task(start_userbot(string_session, user_id))

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """Available commands:
    /ping - Check latency
    /raid <number of messages> - Start raid with random quotes
    /spam <number of messages> <text> - Spam a custom message
    /stop - Stop any ongoing actions (raid, spam, echo, rraid)
    /echo - Continuously echo the message you reply to
    /rraid - Continuously reply with random quotes when the target user sends a message
    """
    await update.message.reply_text(help_text)

# Ping command
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pong!")

# Main bot setup
async def main():
    BOT_TOKEN = '7734408721:AAHwWAuqGoAWrDuKSIstabuRHIaJzltQTaw'  # Replace with your bot token

    # Create application instance
    application = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("clone", clone))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping))

    # Load saved sessions and start userbots
    sessions = load_sessions()
    for user_id, string_session in sessions.items():
        asyncio.create_task(start_userbot(string_session, user_id))

    # Start the bot
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
