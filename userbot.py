import os
import random
import time
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.contacts import ResolveUsernameRequest
from pymongo import MongoClient
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Replace with your bot token
BOT_TOKEN = "7734408721:AAHwWAuqGoAWrDuKSIstabuRHIaJzltQTaw"

# Replace with your Telethon API credentials
API_ID = "27783899"
API_HASH = "30a0620127bd5816e9f5c69e1c426cf5"

# MongoDB setup
MONGO_URI = "mongodb+srv://Cenzo:Cenzo123@cenzo.azbk1.mongodb.net/"
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["user_sessions"]
sessions_collection = db["sessions"]

# Quotes loading
def load_quotes():
    quotes_file = 'chudai.txt'
    if os.path.exists(quotes_file):
        with open(quotes_file, 'r') as file:
            quotes = file.readlines()
        return [quote.strip() for quote in quotes]
    else:
        return ["No text found."]

quotes = load_quotes()

# Userbot session management
user_sessions = {}

async def start_userbot(string_session, user_id):
    client = TelegramClient(StringSession(string_session), API_ID, API_HASH)
    await client.connect()
    
    # Register commands for the user
    @client.on(events.NewMessage(pattern=r'^\.ping$', outgoing=True))
    async def ping(event):
        start_time = time.time()
        end_time = time.time()
        latency = (end_time - start_time) * 1000
        await event.respond(f"Pong! `{latency:.2f} ms`")
        await event.delete()

    @client.on(events.NewMessage(pattern=r'^\.stop$', outgoing=True))
    async def stop(event):
        user_sessions[user_id]["flags"] = {
            "echo_flag": False,
            "rraid_flag": False,
            "raid_flag": False,
            "spam_flag": False
        }
        await event.respond("All ongoing actions stopped.")
        await event.delete()

    @client.on(events.NewMessage(pattern=r'^\.echo$', outgoing=True))
    async def echo(event):
        if event.is_reply:
            target_message = await event.get_reply_message()
            user_sessions[user_id]["target_user_id"] = target_message.sender_id
            user_sessions[user_id]["flags"]["echo_flag"] = True
        else:
            await event.respond("Reply to a message to start echo mode.")
        await event.delete()

    @client.on(events.NewMessage())
    async def monitor_echo(event):
        if user_sessions[user_id]["flags"]["echo_flag"] and event.sender_id == user_sessions[user_id]["target_user_id"]:
            await event.respond(event.text, reply_to=event.id)

    @client.on(events.NewMessage(pattern=r'^\.rraid$', outgoing=True))
    async def rraid(event):
        if event.is_reply:
            target_message = await event.get_reply_message()
            user_sessions[user_id]["target_user_id"] = target_message.sender_id
            user_sessions[user_id]["flags"]["rraid_flag"] = True
        else:
            await event.respond("Reply to a user to start the reply raid.")
            await event.delete()

    @client.on(events.NewMessage())
    async def monitor_rraid(event):
        if user_sessions[user_id]["flags"]["rraid_flag"] and event.sender_id == user_sessions[user_id]["target_user_id"]:
            random_quote = random.choice(quotes)
            await event.respond(random_quote, reply_to=event.message.id)

    @client.on(events.NewMessage(pattern=r'^\.raid (\d+)( @\w+)?$', outgoing=True))
    async def raid(event):
        count = int(event.pattern_match.group(1))
        username = event.pattern_match.group(2)

        if username:
            username = username.strip()[1:]
            try:
                resolved_user = await client(ResolveUsernameRequest(username))
                entity = resolved_user.users[0]
                full_name = f"{entity.first_name} {entity.last_name or ''}".strip()
                for _ in range(count):
                    random_quote = random.choice(quotes)
                    await event.respond(f"<a href='tg://user?id={entity.id}'>{full_name}</a> {random_quote}", parse_mode='html')
                    await asyncio.sleep(1)
            except Exception as e:
                await event.respond(f"Error: Could not resolve username @{username}.")
        else:
            await event.respond("Reply to a message or mention a username for the raid.")
        await event.delete()

    @client.on(events.NewMessage(pattern=r'^\.help$', outgoing=True))
    async def help_command(event):
        help_text = """Available commands:
        .ping - Check latency
        .raid <number> - Start raid with random quotes
        .stop - Stop any ongoing actions
        .echo - Reply to activate echo mode
        .rraid - Reply raid with random quotes
        .help - Show this help
        """
        await event.respond(help_text)
        await event.delete()

    # Save the client instance in the sessions dictionary
    user_sessions[user_id] = {
        "client": client,
        "flags": {
            "echo_flag": False,
            "rraid_flag": False,
            "raid_flag": False,
            "spam_flag": False
        },
        "target_user_id": None
    }

    # Run the client
    await client.run_until_disconnected()

# Bot commands
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Use `/clone <string session>` to start.")

async def clone(update: Update, context: CallbackContext):
    if len(context.args) < 1:
        update.message.reply_text("Usage: /clone <Telethon string session>")
        return

    string_session = context.args[0]
    user_id = update.effective_user.id

    # Check if the session exists
    if sessions_collection.find_one({"user_id": user_id}):
        update.message.reply_text("Your session is already active. Use `/stop` to disconnect.")
        return

    # Save session to MongoDB
    sessions_collection.insert_one({"user_id": user_id, "string_session": string_session})
    update.message.reply_text("Cloning your session...")

    # Start userbot for this user
    asyncio.create_task(start_userbot(string_session, user_id))

async def stop(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if user_id in user_sessions:
        client = user_sessions[user_id]["client"]
        await client.disconnect()
        del user_sessions[user_id]

        sessions_collection.delete_one({"user_id": user_id})
        update.message.reply_text("Disconnected your userbot session.")
    else:
        update.message.reply_text("No active session found.")

# Bot setup
def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("clone", lambda u, c: asyncio.run(clone(u, c))))
    dp.add_handler(CommandHandler("stop", lambda u, c: asyncio.run(stop(u, c))))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
