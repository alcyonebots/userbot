import logging
from pyrogram import Client, filters
import random
from db import quotes  # Ensure you have this import for quotes

# Logging configuration for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global flags and variables
echo_flag = False
rraid_flag = False
raid_flag = False
spam_flag = False
target_user_id = None  # Target user ID for rraid
target_message = None  # Target message for echo and raid

# Ask for the Pyrogram session string
string_session = input("Enter your Pyrogram string session: ")

# Initialize the userbot
app = Client(name="userbot", session_string=string_session)


@app.on_message(filters.regex(r"^\.") & filters.me)
async def handle_dot_command(_, message):
    """Handle commands starting with a dot (.) and delete the command message."""
    command = message.text.split()[0]  # Get the command part

    # Declare the global variables first before using them
    global echo_flag, rraid_flag, raid_flag, spam_flag, target_user_id, target_message

    # Delete the command message after processing
    try:
        await message.delete()

        # Handle the command logic
        if command == ".ping":
            start_time = message.date.timestamp()
            sent_message = await message.reply("Pong!")
            latency = (message.date.timestamp() - start_time) * 1000
            await sent_message.edit_text(f"Pong! `{latency:.2f} ms`")

        elif command == ".echo":
            if message.reply_to_message:
                target_message = message.reply_to_message
                echo_flag = True
                await message.reply("Echo mode activated. Replying to the target message.")
            else:
                await message.reply("Reply to a message to start echo mode.")

        elif command == ".rraid":
            if message.reply_to_message:
                target_user_id = message.reply_to_message.from_user.id
                rraid_flag = True
                await message.reply(f"Reply raid started on user {target_user_id}.")
            else:
                await message.reply("Reply to a message to start the reply raid.")

        elif command == ".stop":
            # Reset all global flags and variables
            echo_flag = False
            rraid_flag = False
            raid_flag = False
            spam_flag = False
            target_user_id = None
            target_message = None
            await message.reply("All actions stopped.")

        elif command == ".spam":
            try:
                args = message.text.split(" ", 2)
                count = int(args[1])
                text = args[2]
                for _ in range(count):
                    await message.reply(text)  # No delay for faster spamming
            except (IndexError, ValueError):
                await message.reply("Usage: .spam <count> <text>")

        elif command == ".raid":
            try:
                args = message.text.split(" ", 1)
                count = int(args[1])
                for _ in range(count):
                    random_quote = random.choice(quotes)
                    await message.reply(random_quote)  # No delay for faster raiding
            except (IndexError, ValueError):
                await message.reply("Usage: .raid <count>")

        elif command == ".help":
            help_text = """Userbot Commands:
            .ping - Check latency
            .echo - Echo messages
            .stop - Stop all actions
            .spam <count> <text> - Spam messages
            .raid <count> - Raid a target with quotes
            .rraid - Reply raid: Reply with random quotes to a target user
            """
            await message.reply(help_text)

    except Exception as e:
        logger.error(f"Error processing command {command}: {e}")


@app.on_message()
async def monitor(_, message):
    """Monitor messages for ongoing actions."""
    global echo_flag, rraid_flag, target_user_id, target_message

    # Echo Mode
    if echo_flag and target_message and message.from_user.id == target_message.from_user.id:
        await message.reply(message.text)

    # Reply Raid Mode
    if rraid_flag and message.from_user and message.from_user.id == target_user_id:
        random_quote = random.choice(quotes)
        await message.reply(random_quote)


# Start the userbot
app.run()
