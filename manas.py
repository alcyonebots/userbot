import logging
from pyrogram import Client, filters
import random
from db import quotes

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


async def start_userbot():
    """Start a userbot for the given session."""
    # Ask for the Pyrogram session string
    string_session = input("Enter your Pyrogram string session: ")
    
    # Initialize the userbot client
    userbot = Client(name="userbot", session_string=string_session)

    @userbot.on_message(filters.command("ping") & filters.me)
    async def ping(_, message):
        """Respond to .ping with latency."""
        start_time = message.date.timestamp()
        sent_message = await message.reply("Pong!")
        latency = (message.date.timestamp() - start_time) * 1000
        await sent_message.edit_text(f"Pong! `{latency:.2f} ms`")

    @userbot.on_message(filters.command("echo") & filters.me)
    async def echo(_, message):
        """Start echo mode."""
        global echo_flag, target_message
        if message.reply_to_message:
            target_message = message.reply_to_message
            echo_flag = True
            await message.reply("Echo mode activated. Replying to the target message.")
        else:
            await message.reply("Reply to a message to start echo mode.")

    @userbot.on_message(filters.command("rraid") & filters.me)
    async def rraid(_, message):
        """Start replying with random quotes to a target user's messages."""
        global rraid_flag, target_user_id

        if message.reply_to_message:
            target_user_id = message.reply_to_message.from_user.id
            rraid_flag = True
            await message.reply(f"Reply raid started on user {target_user_id}.")
        else:
            await message.reply("Reply to a message to start the reply raid.")

    @userbot.on_message(filters.command("stop") & filters.me)
    async def stop(_, message):
        """Stop all ongoing actions."""
        global echo_flag, rraid_flag, raid_flag, spam_flag, target_user_id, target_message
        echo_flag = False
        rraid_flag = False
        raid_flag = False
        spam_flag = False
        target_user_id = None
        target_message = None
        await message.reply("All actions stopped.")

    @userbot.on_message(filters.command("spam") & filters.me)
    async def spam(_, message):
        """Spam a custom message."""
        try:
            args = message.text.split(" ", 2)
            count = int(args[1])
            text = args[2]
            for _ in range(count):
                await message.reply(text)  # No delay for faster spamming
        except (IndexError, ValueError):
            await message.reply("Usage: .spam <count> <text>")

    @userbot.on_message(filters.command("raid") & filters.me)
    async def raid(_, message):
        """Start a raid with random quotes."""
        try:
            args = message.text.split(" ", 1)
            count = int(args[1])

            for _ in range(count):
                random_quote = random.choice(quotes)
                await message.reply(random_quote)  # No delay for faster raiding
        except (IndexError, ValueError):
            await message.reply("Usage: .raid <count>")

    @userbot.on_message(filters.command("help") & filters.me)
    async def help_command(_, message):
        """Show help for userbot commands."""
        help_text = """Userbot Commands:
        .ping - Check latency
        .echo - Echo messages
        .stop - Stop all actions
        .spam <count> <text> - Spam messages
        .raid <count> - Raid a target with quotes
        .rraid - Reply raid: Reply with random quotes to a target user
        """
        await message.reply(help_text)

    @userbot.on_message()
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
    await userbot.start()
    logger.info("Userbot started successfully. Press Ctrl+C to stop.")
    await userbot.idle()


if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(start_userbot())
    except KeyboardInterrupt:
        logger.info("Userbot stopped manually.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
