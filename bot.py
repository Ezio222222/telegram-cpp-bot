import os
import subprocess
import asyncio
import nest_asyncio

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

nest_asyncio.apply()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I am your C++ runner bot.\nSend me C++ code and I will compile and run it."
    )

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text
    with open("code.cpp", "w") as f:
        f.write(code)

    try:
        compile_proc = subprocess.run(
            ["g++", "code.cpp", "-o", "code"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if compile_proc.returncode != 0:
            output = f"❌ Compilation error:\n{compile_proc.stderr}"
        else:
            run_proc = subprocess.run(
                ["./code"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            output = run_proc.stdout or run_proc.stderr or "✅ Program ran with no output."
    except subprocess.TimeoutExpired:
        output = "❌ Execution timed out."

    # Telegram messages max length is 4096 chars; truncate if needed
    await update.message.reply_text(output[:4000])

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_code))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())