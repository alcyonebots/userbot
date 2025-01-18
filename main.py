import os
import random
import time
from telethon import TelegramClient, events
from telegram import Update
from telegram.ext import Updater, CommandHandler
from pymongo import MongoClient
from typing import List

# MongoDB setup
client_mongo = MongoClient("mongodb://localhost:27017/")  # Adjust with your MongoDB URI
db = client_mongo["user_sessions"]
sessions_collection = db["sessions"]

# Telethon setup (replace these with your own details)
API_ID = '27783899'
API_HASH = '30a0620127bd5816e9f5c69e1c426cf5'
BOT_TOKEN = '7734408721:AAHwWAuqGoAWrDuKSIstabuRHIaJzltQTaw'
# Load quotes from an external file
def load_quotes():
    quotes_file = 'chudai.txt'  # Make sure to provide the correct path to the quotes file
    if os.path.exists(quotes_file):
        with open(quotes_file, 'r') as file:
            quotes = file.readlines()
        return [quote.strip() for quote in quotes]
    else:
        return ["No text found."]

quotes = load_quotes()

# MongoDB session existence check and creation
def check_and_create_session(session_name: str):
    if sessions_collection.find_one({"session": session_name}):
        return False  # Session already exists
    # Create the session and store it in the database
    sessions_collection.insert_one({"session": session_name})
    return True

# Start the bot using python-telegram-bot
def start_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add the command handler for /clone and /start
    dp.add_handler(CommandHandler('clone', clone_session))
    dp.add_handler(CommandHandler('start', start))

    # Add the userbot-related events to the dispatcher
    dp.add_handler(CommandHandler('ping', ping))
    dp.add_handler(CommandHandler('stop', stop))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('echo', echo))
    dp.add_handler(CommandHandler('raid', raid))
    dp.add_handler(CommandHandler('rraid', rraid))

    # Start the bot
    updater.start_polling()
    updater.idle()

# Bot to handle /clone command
def clone_session(update: Update, context):
    if context.args:
        session_name = context.args[0]
        try:
            # Create a new TelegramClient instance
            client = TelegramClient(session_name, API_ID, API_HASH)
            client.start()
            if check_and_create_session(session_name):
                update.message.reply_text(f"Session cloned successfully!")
            else:
                update.message.reply_text(f"Session already exists.")
        except Exception as e:
            update.message.reply_text(f"Error with session {str(e)}")
    else:
        update.message.reply_text("Please provide a telethon session. Usage: /clone <telethon session>")

# Start command handler to welcome users
def start(update: Update, context):
    start_message = """Welcome to the Telethon Userbot!
Here are the available commands:
- `/clone <session>` - Clone your session
- `.ping` - Check latency
- `.raid <number of messages>` - Start raid with random quotes
- `.spam <number of messages> <text>` - Spam a custom message
- `.stop` - Stop any ongoing actions (raid or spam)
- `.echo` - Echo the message you reply to
- `.rraid` - Reply with random quotes to a mentioned user
"""
    update.message.reply_text(start_message)

# Telethon Userbot (for handling commands like .ping, .raid, etc.)
async def ping(event):
    start_time = time.time()
    await event.respond("Pong!")
    end_time = time.time()
    latency = (end_time - start_time) * 1000  # Convert to ms
    await event.respond(f"Pong! `{latency:.2f} ms`")
    await event.delete()  # Delete the command message

@client.on(events.NewMessage(pattern=r'^\.ping$', outgoing=True))
async def ping_handler(event):
    await ping(event)

# Handle .stop (to stop any ongoing raids or spams)
async def stop(event):
    global stop_flag
    stop_flag = True
    await event.respond("All ongoing actions stopped.")
    await event.delete()  # Delete the command message

# Echo handler
async def echo(event):
    if event.is_reply:
        original_message = await event.get_reply_message()
        await event.respond(original_message.text)
        await event.delete()  # Delete the command message
    else:
        await event.respond("Reply to a message to echo it.")
        await event.delete()

# Raid handler (.raid)
async def raid(event, number_of_messages: int, target_user: str):
    stop_flag = False
    for _ in range(number_of_messages):
        if stop_flag:
            break
        random_quote = random.choice(quotes)
        await event.respond(f"{target_user} {random_quote}")
        await event.delete()  # Delete the command message

# Spam handler (.spam)
async def spam(event, number_of_messages: int, text: str):
    stop_flag = False
    for _ in range(number_of_messages):
        if stop_flag:
            break
        await event.respond(text)
        await event.delete()  # Delete the command message

# Random raid handler (.rraid)
@client.on(events.NewMessage(pattern=r'^\.rraid$', outgoing=True))
async def rraid(event):
    if event.is_reply:
        target_user = await event.get_reply_message()
        random_quote = random.choice(quotes)
        await event.respond(f"@{target_user.sender.username} {random_quote}")
        await event.delete()  # Delete the command message
    else:
        await event.respond("Reply to a message to send a random quote.")
        await event.delete()  # Delete the command message

# Help command handler (.help)
async def help(event):
    help_text = """Available commands:
    .ping - Check latency
    .raid <number of messages> - Start raid with random quotes
    .spam <number of messages> <text> - Spam a custom message
    .stop - Stop any ongoing actions (raid or spam)
    .echo - Echo the message you reply to
    .rraid - Reply with random quotes to a mentioned user
    """
    await event.respond(help_text)
    await event.delete()  # Delete the command message

# Main method to initialize both TelegramBot and Telethon userbot
if __name__ == "__main__":
    # Start the Telethon client
    userbot = TelegramClient('userbot', API_ID, API_HASH)
    userbot.start()

    # Start the Telegram bot
    start_bot()

    # Run the Telethon client in the background
    userbot.run_until_disconnected()
