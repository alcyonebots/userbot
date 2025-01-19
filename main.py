import os
import random
import time
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.functions.users import GetFullUserRequest
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import pymongo

# Telethon setup (replace these with your own details)
API_ID = '27783899'
API_HASH = '30a0620127bd5816e9f5c69e1c426cf5'

# MongoDB setup for storing sessions
client = pymongo.MongoClient("mongodb+srv://Cenzo:Cenzo123@cenzo.azbk1.mongodb.net/")
db = client["userbot_sessions"]
sessions_collection = db["sessions"]

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Global flags and variables
echo_flag = False
rraid_flag = False
raid_flag = False
spam_flag = False
target_user_id = None  # Target user ID for rraid
target_message = None  # Target message for echo and raid

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

# Function to start the userbot with a string session
async def start_userbot(string_session):
    userbot = TelegramClient(StringSession(string_session), API_ID, API_HASH)
  
    @userbot.on(events.NewMessage(pattern=r'^\.ping$', outgoing=True))
    async def ping(event):
        start_time = time.time()
        await asyncio.sleep(0)  # Simulate latency calculation
        end_time = time.time()
        latency = (end_time - start_time) * 1000  # Convert to ms
        await event.respond(f"Pong! `{latency:.2f} ms`")
        await event.delete()

    @userbot.on(events.NewMessage(pattern=r'^\.stop$', outgoing=True))
    async def stop(event):
        global echo_flag, rraid_flag, raid_flag, spam_flag, target_user_id, target_message
        echo_flag = False
        rraid_flag = False
        raid_flag = False
        spam_flag = False
        target_user_id = None
        target_message = None
        await event.respond("All ongoing actions stopped.")
        await event.delete()

    @userbot.on(events.NewMessage(pattern=r'^\.echo$', outgoing=True))
    async def echo(event):
        global echo_flag, target_user_id
        if event.is_reply:
            target_message = await event.get_reply_message()
            target_user_id = target_message.sender_id  # Save the target user's ID
            echo_flag = True
        else:
            await event.respond("Reply to a message to start echo mode.")
        await event.delete()

    @userbot.on(events.NewMessage())
    async def monitor_echo(event):
        global echo_flag, target_user_id
        if echo_flag and event.sender_id == target_user_id:
            try:
                message_text = event.text
                await event.respond(message_text, reply_to=event.id)
            except Exception as e:
                print(f"Error during echo: {e}")

    @userbot.on(events.NewMessage(pattern=r'^\.rraid$', outgoing=True))
    async def rraid(event):
        global rraid_flag, target_user_id
        if event.is_reply:
            rraid_flag = True
            target_message = await event.get_reply_message()
            target_user_id = target_message.sender_id
        else:
            await event.respond("Reply to a user to start the reply raid.")
            await event.delete()

    @userbot.on(events.NewMessage())
    async def monitor(event):
        global rraid_flag, target_user_id
        if rraid_flag and event.sender_id == target_user_id:
            random_quote = random.choice(quotes)
            await event.respond(random_quote, reply_to=event.message.id)

    @userbot.on(events.NewMessage(pattern=r'^\.raid (\d+)( @\w+)?$', outgoing=True))
    async def raid(event):
        global raid_flag
        raid_flag = True
        count = int(event.pattern_match.group(1))
        username = event.pattern_match.group(2)

        if username:
            username = username.strip()[1:]
            try:
                resolved_user = await userbot(ResolveUsernameRequest(username))
                entity = resolved_user.users[0]
                target_user_id = entity.id
                first_name = entity.first_name
                last_name = entity.last_name or ''
                full_name = f"{first_name} {last_name}".strip()

                for _ in range(count):
                    if not raid_flag:
                        break
                    random_quote = random.choice(quotes)
                    await event.respond(f"<a href='tg://user?id={target_user_id}'>{full_name}</a> {random_quote}", parse_mode='html')
                    await asyncio.sleep(0)
            except Exception as e:
                await event.respond(f"Error: Could not resolve username @{username}.")
        elif event.is_reply:
            try:
                target_message = await event.get_reply_message()
                target_user = target_message.sender
                first_name = target_user.first_name
                last_name = target_user.last_name or ''
                full_name = f"{first_name} {last_name}".strip()

                for _ in range(count):
                    if not raid_flag:
                        break
                    random_quote = random.choice(quotes)
                    await event.respond(f"<a href='tg://user?id={target_user.id}'>{full_name}</a> {random_quote}", parse_mode='html')
                    await asyncio.sleep(0)
            except Exception as e:
                await event.respond("Error: Could not retrieve the target user.")
        else:
            await event.respond("You need to reply to a message or mention a username for the raid.")
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
            await asyncio.sleep(0)
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

    # Start the userbot
    await userbot.start()
    print(f"Userbot started for session: {string_session}")
    await userbot.run_until_disconnected()

async def load_sessions():
    """Load all sessions from MongoDB and start userbots."""
    try:
        saved_sessions = sessions_collection.find()  # Fetch all saved sessions
        for session in saved_sessions:
            string_session = session.get("string_session")
            if string_session:
                # Start a new event loop for each userbot
                asyncio.create_task(start_userbot(string_session))
    except Exception as e:
        logger.error(f"Error loading sessions: {e}")

def clone(update: Update, context):
    try:
        # Parse the session string from the command
        if not context.args or len(context.args) == 0:
            update.message.reply_text("Please provide a valid Telethon string session.")
            return

        string_session = context.args[0]

        # Save the session string in MongoDB for the user
        user_id = update.message.from_user.id
        sessions_collection.update_one(
            {"user_id": user_id},
            {"$set": {"string_session": string_session}},
            upsert=True
        )

        update.message.reply_text("Session cloned successfully! Starting your userbot...")

        # Run the userbot in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_userbot(string_session))
    except Exception as e:
        logger.error(f"Error in /clone command: {e}")
        update.message.reply_text(f"An error occurred: {e}")

# Help command
def help_command(update: Update, context):
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
def ping(update: Update, context):
    update.message.reply_text("Pong!")

# Main bot setup
def main():
    BOT_TOKEN = '7734408721:AAHwWAuqGoAWrDuKSIstabuRHIaJzltQTaw'
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("clone", clone))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("ping", ping))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
