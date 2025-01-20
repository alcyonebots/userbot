import asyncio
import random
from datetime import datetime
from pyrogram import Client, filters
from utils import load_quotes

# Store userbot clients dynamically
userbots = {}
quotes = load_quotes()

# Global flags for each user
user_flags = {}


async def start_userbot(string_session, user_id):
    """Start a Pyrogram client for the given session string and user."""
    userbot = Client(
        name=f"userbot_{user_id}",
        session_string=string_session,
        api_id=27783899,
        api_hash="30a0620127bd5816e9f5c69e1c426cf5",
    )

    # Initialize user flags
    user_flags[user_id] = {
        "echo_flag": False,
        "rraid_flag": False,
        "raid_flag": False,
        "spam_flag": False,
        "target_user_id": None,
        "target_message": None,
    }

    @userbot.on_message(filters.command("ping") & filters.me)
    async def ping(_, message):
        """Calculate and show latency."""
        start_time = datetime.now()
        sent_message = await message.reply_text("Pinging...")
        end_time = datetime.now()
        latency = (end_time - start_time).total_seconds() * 1000  # Convert to ms
        await sent_message.edit_text(f"Pong! 🏓 `{latency:.2f} ms`")

    @userbot.on_message(filters.command("stop") & filters.me)
    async def stop(_, message):
        """Stop all ongoing actions."""
        flags = user_flags[user_id]
        for key in flags:
            if key.endswith("_flag"):
                flags[key] = False
        flags["target_user_id"] = None
        flags["target_message"] = None
        await message.reply_text("All ongoing actions stopped.")

    @userbot.on_message(filters.command("echo") & filters.me)
    async def echo(_, message):
        """Enable echo mode."""
        flags = user_flags[user_id]
        if message.reply_to_message:
            flags["target_message"] = message.reply_to_message
            flags["target_user_id"] = message.reply_to_message.from_user.id
            flags["echo_flag"] = True
            await message.reply_text("Echo mode enabled.")
        else:
            await message.reply_text("Reply to a message to start echo mode.")

    @userbot.on_message(filters.command("rraid") & filters.me)
    async def rraid(_, message):
        """Enable reply raid."""
        flags = user_flags[user_id]
        if message.reply_to_message:
            flags["target_message"] = message.reply_to_message
            flags["target_user_id"] = message.reply_to_message.from_user.id
            flags["rraid_flag"] = True
            await message.reply_text("Reply raid enabled.")
        else:
            await message.reply_text("Reply to a user to start the raid.")

    @userbot.on_message(filters.text & ~filters.me)
    async def monitor(_, message):
        """Monitor user messages for echo and rraid."""
        flags = user_flags[user_id]
        if flags["echo_flag"] and message.from_user.id == flags["target_user_id"]:
            await message.reply_text(message.text)
        elif flags["rraid_flag"] and message.from_user.id == flags["target_user_id"]:
            random_quote = random.choice(quotes)
            await message.reply_text(random_quote)

    @userbot.on_message(filters.command("raid", prefixes=".") & filters.me)
    async def raid(_, message):
        """Perform a raid by sending random quotes."""
        flags = user_flags[user_id]
        if flags["raid_flag"]:
            await message.reply_text("A raid is already ongoing.")
            return

        args = message.text.split(maxsplit=2)
        if len(args) < 2:
            await message.reply_text("Usage: .raid <count> [@username or reply]")
            return

        try:
            count = int(args[1])
            target_id = None
            target_name = None

            if len(args) == 3 and args[2].startswith("@"):
                target_name = args[2][1:]
            elif message.reply_to_message:
                target_id = message.reply_to_message.from_user.id
                target_name = message.reply_to_message.from_user.first_name

            if not (target_id or target_name):
                await message.reply_text("Provide a username or reply to a message.")
                return

            flags["raid_flag"] = True
            for _ in range(count):
                if not flags["raid_flag"]:
                    break
                random_quote = random.choice(quotes)
                if target_id:
                    await message.reply_text(
                        f"<a href='tg://user?id={target_id}'>{target_name}</a>: {random_quote}",
                        parse_mode="html",
                    )
                else:
                    await message.reply_text(f"@{target_name}: {random_quote}")
                await asyncio.sleep(1)

            flags["raid_flag"] = False
        except ValueError:
            await message.reply_text("The count must be a number.")

    @userbot.on_message(filters.command("spam", prefixes=".") & filters.me)
    async def spam(_, message):
        """Spam custom text a specified number of times."""
        flags = user_flags[user_id]
        if flags["spam_flag"]:
            await message.reply_text("Spam is already ongoing.")
            return

        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.reply_text("Usage: .spam <count> <text>")
            return

        try:
            count = int(args[1])
            text = args[2]
            flags["spam_flag"] = True

            for _ in range(count):
                if not flags["spam_flag"]:
                    break
                await message.reply_text(text)
                await asyncio.sleep(1)

            flags["spam_flag"] = False
        except ValueError:
            await message.reply_text("The count must be a number.")

    @userbot.on_message(filters.command("help") & filters.me)
    async def help_command(_, message):
        """Show help message."""
        help_text = """Available commands:
        .ping - Check latency
        .stop - Stop all ongoing actions
        .echo - Echo messages from a specific user
        .rraid - Reply raid with random quotes
        .raid <count> [@username or reply] - Send random quotes
        .spam <count> <text> - Spam custom text
        .help - Show this help message
        """
        await message.reply_text(help_text)

    # Start the userbot
    await userbot.start()
    userbots[user_id] = userbot
    print(f"Userbot started for user_id: {user_id}")
    await userbot.idle()
