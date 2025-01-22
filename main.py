import logging
from pyrogram import Client, filters
import random
import asyncio

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global flags and variables
echo_flag = False
rraid_flag = False
raid_flag = False
target_username = None
target_message = None

# Load quotes from files
try:
    with open("raid.txt", "r") as raid_file:
        RAID = raid_file.read().splitlines()
    with open("rraid.txt", "r") as rraid_file:
        REPLYRAID = rraid_file.read().splitlines()
except FileNotFoundError as e:
    logger.error(f"Error loading quotes: {e}")
    RAID = []
    REPLYRAID = []

# Pyrogram session string
string_session = input("Enter your Pyrogram string session: ")

# Initialize the userbot
app = Client(name="userbot", session_string=string_session)


@app.on_message(filters.regex(r"^\.") & filters.me)
async def handle_dot_command(_, message):
    global echo_flag, rraid_flag, raid_flag, target_username, target_message

    command = message.text.split()[0]
    args = message.text.split()[1:]

    try:
        # Automatically delete the command message
        await message.delete()

        if command == ".ping":
            start_time = message.date.timestamp()
            sent_message = await message.reply("Pong!")
            latency = (message.date.timestamp() - start_time) * 1000
            await sent_message.edit_text(f"Pong! `{latency:.2f} ms`")

        elif command == ".echo":
            if message.reply_to_message:
                target_message = message.reply_to_message
                echo_flag = True
            elif len(args) == 1:
                target_username = args[0].lstrip("@")
                echo_flag = True
            else:
                await message.reply("Usage: `.echo <@username or reply to a message>`")

        elif command == ".rraid":
            if message.reply_to_message:
                target_message = message.reply_to_message
                rraid_flag = True
            elif len(args) == 1:
                target_username = args[0].lstrip("@")
                rraid_flag = True
            else:
                await message.reply("Usage: `.rraid <@username or reply to a message>`")

        elif command == ".raid":
            if len(args) >= 2:
                count = int(args[0])
                target_username = args[1].lstrip("@") if len(args) > 1 else None

                if message.reply_to_message:
                    target_message = message.reply_to_message
                    for _ in range(count):
                        random_quote = random.choice(RAID) if RAID else "No RAID quotes available."
                        target_mention = target_message.from_user.mention
                        await message.reply(f"{target_mention} {random_quote}")
                        await asyncio.sleep(0.1)
                elif target_username:
                    # Get user details to fetch mention
                    user = await app.get_users(target_username)
                    user_mention = user.mention if user else f"@{target_username}"  # Fallback if mention not found
                    for _ in range(count):
                        random_quote = random.choice(RAID) if RAID else "No RAID quotes available."
                        await message.reply(f"{user_mention} {random_quote}")
                        await asyncio.sleep(0.1)
                else:
                    await message.reply("Usage: `.raid <count> <@username or reply to a message>`")
            else:
                await message.reply("Usage: `.raid <count> <@username or reply to a message>`")

        elif command == ".stop":
            echo_flag = False
            rraid_flag = False
            raid_flag = False
            target_username = None
            target_message = None

        elif command == ".spam":
            if len(args) >= 2:
                count = int(args[0])
                text = " ".join(args[1:])
                for _ in range(count):
                    await message.reply(text)
                    await asyncio.sleep(0.1)  # Avoid rate limits
            else:
                await message.reply("Usage: `.spam <count> <text>`")

        elif command == ".help":
            help_text = """Userbot Commands:
            .ping - Check latency
            .echo <@username or reply> - Echo a message
            .stop - Stop all actions
            .spam <count> <text> - Spam messages
            .raid <count> <@username or reply> - Raid a target with quotes
            .rraid <@username or reply> - Reply raid with random quotes
            """
            await message.reply(help_text)

    except Exception as e:
        logger.error(f"Error processing command {command}: {e}")


@app.on_message()
async def monitor(_, message):
    global echo_flag, rraid_flag, target_username, target_message

    # Echo Mode
    if echo_flag and target_message and (
        (message.reply_to_message and message.reply_to_message == target_message)
        or (message.from_user.username == target_username)
    ):
        await message.reply(message.text)

    # Reply Raid Mode (rraid)
    if rraid_flag and (
        (message.reply_to_message and message.reply_to_message == target_message)
        or (message.from_user and message.from_user.username == target_username)
    ):
        random_quote = random.choice(REPLYRAID) if REPLYRAID else "No REPLYRAID quotes available."
        await message.reply(random_quote)

    # Raid Mode (raid)
    if raid_flag and (
        (message.reply_to_message and message.reply_to_message == target_message)
        or (message.from_user and message.from_user.username == target_username)
    ):
        random_quote = random.choice(RAID) if RAID else "No RAID quotes available."
        if target_message:
            target_mention = target_message.from_user.mention
            await message.reply(f"{target_mention} {random_quote}")
        elif target_username:
            await message.reply(f"@{target_username} {random_quote}")


# Start the userbot
app.run()
