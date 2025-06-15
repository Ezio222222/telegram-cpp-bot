import asyncio
import os
import subprocess
import nest_asyncio

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Apply nested async support for environments like Railway
nest_asyncio.apply()

# Load the bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am a Telegram bot created by Ezio. Send your C++ code to see output.")

# Handle incoming messages as C++ code
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text
    with open("code.cpp", "w") as f:
        f.write(code)

    try:
        compile_result = subprocess.run(
            ["g++", "code.cpp", "-o", "code"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if compile_result.returncode != 0:
            output = f"❌ Compilation Error:\n{compile_result.stderr}"
        else:
            run_result = subprocess.run(
                ["./code"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            output = run_result.stdout or run_result.stderr or "✅ Program ran but returned no output."
    except subprocess.TimeoutExpired:
        output = "❌ Execution timed out."

    await update.message.reply_text(output[:4000])

# Main entry point
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_code))
    await app.run_polling()

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())