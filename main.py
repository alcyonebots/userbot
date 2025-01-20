import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from utils import load_sessions, clone, help_command, ping

async def main():
    BOT_TOKEN = '7734408721:AAHwWAuqGoAWrDuKSIstabuRHIaJzltQTaw'

    # Build the bot application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("clone", clone))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ping", ping))

    # Start the bot in a separate task
    bot_task = asyncio.create_task(app.run_polling())

    # Load user sessions asynchronously
    await load_sessions()

    # Keep the bot and user sessions running
    await bot_task

if __name__ == "__main__":
    asyncio.run(main())
