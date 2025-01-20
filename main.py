from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import asyncio
from userbot import start_userbot
from db import load_sessions, save_session

# Clone command for the bot
async def clone(update: Update, context: CallbackContext):
    try:
        if not context.args or len(context.args) == 0:
            update.message.reply_text("Please provide a valid Telethon string session.")
            return

        string_session = context.args[0]

        # Save the session string in MongoDB for the user
        user_id = update.message.from_user.id
        save_session(user_id, string_session)

        update.message.reply_text("Session cloned successfully! Starting your userbot...")

        # Start the userbot for this session
        asyncio.create_task(start_userbot(string_session, user_id))

    except Exception as e:
        update.message.reply_text(f"An error occurred: {e}")

# Help command
def help_command(update: Update, context: CallbackContext):
    help_text = """Available commands:
    /ping - Check latency
    /raid <number of messages> - Start raid with random quotes
    /spam <number of messages> <text> - Spam a custom message
    /stop - Stop any ongoing actions (raid, spam, echo, rraid)
    /echo - Continuously echo the message you reply to
    /rraid - Continuously reply with random quotes when the target user sends a message
    """
    update.message.reply_text(help_text)

# Ping command
def ping(update: Update, context: CallbackContext):
    update.message.reply_text("Pong!")

# Main bot setup
def main():
    BOT_TOKEN = 'YOUR_BOT_TOKEN'  # Replace with your bot token
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("clone", clone))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("ping", ping))

    # Start the Telegram bot
    updater.start_polling()

    # Load saved sessions and start userbots
    loop = asyncio.get_event_loop()
    loop.run_until_complete(load_sessions())

    # Run idle to keep the bot running
    updater.idle()

if __name__ == '__main__':
    main()
