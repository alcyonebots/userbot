import os
import random
import time
import asyncio
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from pymongo import MongoClient

# MongoDB setup
client_mongo = MongoClient("mongodb+srv://Cenzo:Cenzo123@cenzo.azbk1.mongodb.net/")  # Adjust with your MongoDB URI
db = client_mongo["user_sessions"]
sessions_collection = db["sessions"]

# Telethon setup (replace these with your own details)
API_ID = '27783899'
API_HASH = '30a0620127bd5816e9f5c69e1c426cf5'
BOT_TOKEN = '7734408721:AAHwWAuqGoAWrDuKSIstabuRHIaJzltQTaw'

# Global flags and variables
echo_flag = False
rraid_flag = False
raid_flag = False
spam_flag = False
target_user_id = None  # Target user ID for rraid

# Load quotes from an external file
def load_quotes():
    quotes_file = 'chudai.txt'  # Path to the quotes file
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
    sessions_collection.insert_one({"session": session_name})
    return True

# Start the bot using python-telegram-bot
def start_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add the command handler for /clone and /start
    dp.add_handler(CommandHandler('clone', clone_session))
    dp.add_handler(CommandHandler('start', start))

    # Start the bot
    updater.start_polling()
    updater.idle()

# Handle /clone command for string session
async def clone_session(update: Update, context: CallbackContext):
    if context.args:
        string_session = context.args[0]  # Get the string session
        try:
            # Create a new TelegramClient using the string session
            client = TelegramClient('string_session_client', API_ID, API_HASH)
            client.session = string_session  # Use the string session directly

            # Start the client session with the provided string session
            await client.start()  # Use await for asynchronous start

            # If successful, reply to the user
            if check_and_create_session(string_session):
                await update.message.reply_text(f"Telethon string session cloned successfully!")
            else:
                await update.message.reply_text(f"Telethon string session already exists.")
        except SessionPasswordNeededError:
            await update.message.reply_text(f"Please enter your 2FA password to continue.")
        except Exception as e:
            await update.message.reply_text(f"Error with string session: {str(e)}")
    else:
        await update.message.reply_text("Please provide a Telethon string session. Usage: /clone <string_session>")

# Start command handler to welcome users
async def start(update: Update, context: CallbackContext):
    start_message = """Welcome to the Telethon Userbot!
Here are the available commands:
- `/clone <string_session>` - Clone your session"""

    await update.message.reply_text(start_message)

# Telethon Userbot
userbot = TelegramClient('userbot', API_ID, API_HASH)

@userbot.on(events.NewMessage(pattern=r'^\.ping$', outgoing=True))
async def ping(event):
    start_time = time.time()
    await event.respond("Pong!")
    end_time = time.time()
    latency = (end_time - start_time) * 1000  # Convert to ms
    await event.respond(f"Pong! `{latency:.2f} ms`")
    await event.delete()

@userbot.on(events.NewMessage(pattern=r'^\.stop$', outgoing=True))
async def stop(event):
    global echo_flag, rraid_flag, raid_flag, spam_flag, target_user_id
    echo_flag = False
    rraid_flag = False
    raid_flag = False
    spam_flag = False
    target_user_id = None
    await event.respond("All ongoing actions stopped.")
    await event.delete()

@userbot.on(events.NewMessage(pattern=r'^\.echo$', outgoing=True))
async def echo(event):
    global echo_flag
    if event.is_reply:
        echo_flag = True
        original_message = await event.get_reply_message()
        await event.respond("Echo mode activated.")
        while echo_flag:
            await event.respond(original_message.text)
            await asyncio.sleep(2)
    else:
        await event.respond("Reply to a message to start echo mode.")
    await event.delete()

@userbot.on(events.NewMessage(pattern=r'^\.rraid$', outgoing=True))
async def rraid(event):
    global rraid_flag, target_user_id
    if event.is_reply:
        rraid_flag = True
        target_message = await event.get_reply_message()
        target_user_id = target_message.sender_id
        await event.respond("Reply Raid activated.")
        await event.delete()
    else:
        await event.respond("Reply to a user to start the reply raid.")
        await event.delete()

@userbot.on(events.NewMessage())
async def monitor(event):
    global rraid_flag, target_user_id
    if rraid_flag and event.sender_id == target_user_id:
        random_quote = random.choice(quotes)
        await event.respond(random_quote)

@userbot.on(events.NewMessage(pattern=r'^\.raid (\d+)$', outgoing=True))
async def raid(event):
    global raid_flag
    raid_flag = True
    if event.is_reply:
        count = int(event.pattern_match.group(1))
        target_message = await event.get_reply_message()
        target_user = target_message.sender_id
        await event.respond(f"Raid started!")
        for _ in range(count):
            if not raid_flag:
                break
            random_quote = random.choice(quotes)
            await event.respond(f"@{target_user} {random_quote}")
            await asyncio.sleep(1)
    else:
        await event.respond("Reply to a user to raid them.")
    await event.delete()

@userbot.on(events.NewMessage(pattern=r'^\.spam (\d+) (.+)$', outgoing=True))
async def spam(event):
    global spam_flag
    spam_flag = True
    count = int(event.pattern_match.group(1))
    text = event.pattern_match.group(2)
    for _ in range(count):
        if not spam_flag:
            break
        await event.respond(text)
        await asyncio.sleep(1)
    await event.delete()

@userbot.on(events.NewMessage(pattern=r'^\.help$', outgoing=True))
async def help_command(event):
    help_text = """Available commands:
    .ping - Check latency
    .raid <number of messages> - Start raid with random quotes
    .spam <number of messages> <text> - Spam a custom message
    .stop - Stop any ongoing actions (raid, spam, echo, rraid)
    .echo - Continuously echo the message you reply to
    .rraid - Continuously reply with random quotes when the target user sends a message
    """
    await event.respond(help_text)
    await event.delete()

# Main method to initialize both TelegramBot and Telethon userbot
async def main():
    # Start the Telethon client in a background task
    userbot.start()

    # Start the Telegram bot asynchronously
    start_bot()

    # Run the Telethon client
    await userbot.run_until_disconnected()

# Run everything asynchronously
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
