import os
import random
import time
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.functions.users import GetFullUserRequest

# Telethon setup (replace these with your own details)
API_ID = '27783899'
API_HASH = '30a0620127bd5816e9f5c69e1c426cf5'

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

# Ask for Telethon string session in the console
string_session = input("Enter your Telethon string session: ")

# Telethon Userbot using the string session
userbot = TelegramClient(StringSession(string_session), API_ID, API_HASH)

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
    global echo_flag, target_message
    if event.is_reply:
        echo_flag = True
        target_message = await event.get_reply_message()
        await event.respond("Echo mode activated.")
        while echo_flag:
            await event.respond(target_message.text)
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
        await event.respond(f"Reply Raid activated. Now replying to messages from the target user.")
        await event.delete()
    else:
        await event.respond("Reply to a user to start the reply raid.")
        await event.delete()

@userbot.on(events.NewMessage())
async def monitor(event):
    global rraid_flag, target_user_id
    if rraid_flag and event.sender_id == target_user_id:
        random_quote = random.choice(quotes)
        # Send quote while replying to the target user
        await event.respond(random_quote, reply_to=event.message.id)

@userbot.on(events.NewMessage(pattern=r'^\.raid (\d+)( @\w+)?$', outgoing=True))
async def raid(event):
    global raid_flag, target_message
    raid_flag = True
    count = int(event.pattern_match.group(1))
    username = event.pattern_match.group(2)

    if username:  # If a username is provided (e.g., @username)
        username = username.strip()  # Remove the '@' symbol
        username = username[1:]  # Strip the leading '@' symbol
        
        try:
            # Try to resolve the username to get the user ID
            resolved_user = await userbot(ResolveUsernameRequest(username))
            target_user = resolved_user.user.id
            
            # Retrieve the full user information
            full_user = await userbot(GetFullUserRequest(target_user))
            first_name = full_user.first_name
            last_name = full_user.last_name or ''  # Use empty string if no last name

            # Construct the user's full name (first + last name)
            full_name = f"{first_name} {last_name}".strip()

            await event.respond(f"Raid started for <a href='tg://user?id={target_user}'>{full_name}</a>!")
            for _ in range(count):
                if not raid_flag:
                    break
                random_quote = random.choice(quotes)
                # Send the quote mentioning the user by their full name
                await event.respond(f"<a href='tg://user?id={target_user}'>{full_name}</a> {random_quote}", parse_mode='html')
                await asyncio.sleep(1)
        except Exception as e:
            await event.respond(f"Error: Could not resolve username @{username}.")
            return
    elif event.is_reply:  # If no username is provided, use the replied user's ID
        target_message = await event.get_reply_message()
        target_user = target_message.sender_id

        # Retrieve the full user information
        full_user = await userbot(GetFullUserRequest(target_user))
        first_name = full_user.first_name
        last_name = full_user.last_name or ''  # Use empty string if no last name

        # Construct the user's full name (first + last name)
        full_name = f"{first_name} {last_name}".strip()

        await event.respond(f"Raid started for <a href='tg://user?id={target_user}'>{full_name}</a>!")
        for _ in range(count):
            if not raid_flag:
                break
            random_quote = random.choice(quotes)
            # Send the quote mentioning the user by their full name
            await event.respond(f"<a href='tg://user?id={target_user}'>{full_name}</a> {random_quote}", parse_mode='html', reply_to=target_message.id)
            await asyncio.sleep(1)
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

# Main method to initialize Telethon userbot
async def main():
    # Start the Telethon client in a background task
    await userbot.start()

    # Run the Telethon client
    await userbot.run_until_disconnected()

# Run everything asynchronously
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
