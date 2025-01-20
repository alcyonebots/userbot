from pyrogram import Client, filters
import random
import asyncio
from db import quotes

# Global flags and variables
echo_flag = False
rraid_flag = False
raid_flag = False
spam_flag = False
target_user_id = None  # Target user ID for rraid
target_message = None  # Target message for echo and raid


async def start_userbot(string_session, user_id):
    """Start a userbot for a given session."""
    app = Client(name=f"userbot_{user_id}", session_string=string_session)

    @app.on_message(filters.command("ping") & filters.me)
    async def ping(_, message):
        """Respond to .ping with latency."""
        start_time = asyncio.get_event_loop().time()
        sent_message = await message.reply("Pong!")
        latency = (asyncio.get_event_loop().time() - start_time) * 1000
        await sent_message.edit_text(f"Pong! `{latency:.2f} ms`")

    @app.on_message(filters.command("echo") & filters.me)
    async def echo(_, message):
        """Start echo mode."""
        global echo_flag, target_message
        if message.reply_to_message:
            target_message = message.reply_to_message
            echo_flag = True
            await message.reply("Echo mode activated. Replying to the target message.")
        else:
            await message.reply("Reply to a message to start echo mode.")

    @app.on_message(filters.command("rraid") & filters.me)
    async def rraid(_, message):
        """Start replying with random quotes to a target user's messages."""
        global rraid_flag, target_user_id

        if message.reply_to_message:
            target_user_id = message.reply_to_message.from_user.id
            rraid_flag = True
            await message.reply(f"Reply raid started on user {target_user_id}.")
        else:
            await message.reply("Reply to a message to start the reply raid.")

    @app.on_message(filters.command("stop") & filters.me)
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

    @app.on_message(filters.command("spam") & filters.me)
    async def spam(_, message):
        """Spam a custom message."""
        global spam_flag
        try:
            args = message.text.split(" ", 2)
            count = int(args[1])
            text = args[2]
            spam_flag = True
            for _ in range(count):
                if not spam_flag:
                    break
                await message.reply(text)
                await asyncio.sleep(1)
        except (IndexError, ValueError):
            await message.reply("Usage: .spam <count> <text>")

    @app.on_message(filters.command("raid") & filters.me)
    async def raid(_, message):
        """Start a raid with random quotes."""
        global raid_flag
        try:
            args = message.text.split(" ", 1)
            count = int(args[1])
            raid_flag = True

            for _ in range(count):
                if not raid_flag:
                    break
                random_quote = random.choice(quotes)
                await message.reply(random_quote)
                await asyncio.sleep(1)
        except (IndexError, ValueError):
            await message.reply("Usage: .raid <count>")

    @app.on_message(filters.command("help") & filters.me)
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

    app.run()
