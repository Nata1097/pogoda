import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a friendly welcome message when the user types /start."""
    await update.message.reply_text(
        "Hi! I'm your Weather & Outfit Assistant.\n"
        "Soon I will help you choose the perfect outfit based on the current weather!"
    )

def main():
    """Starts the Telegram bot."""
    print("Starting bot...")
    
    # Create bot application
    application = Application.builder().token(TOKEN).build()

    # Register /start command handler
    application.add_handler(CommandHandler("start", start_command))

    # Run the bot until you press Ctrl-C
    print("Bot is running. Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == "__main__":
    main()