import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from weather_api import get_current_weather

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a friendly welcome message when the user types /start."""
    await update.message.reply_text(
        "Hi! I'm your Weather and Outfit Assistant.\n"
        "Type /weather to see the current conditions!"
    )

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetches real-time weather and sends it to the user."""
    await update.message.reply_text("Fetching current weather data... Please wait.")
    
    try:
        data = get_current_weather()
        
        response = (
            f"CURRENT WEATHER REPORT\n\n"
            f"Time: {data['timestamp']}\n"
            f"Temperature: {data['temperature']} C\n"
            f"Feels like: {data['apparent_temperature']} C\n"
            f"Wind Speed: {data['wind_speed']} km/h"
        )
        
        # Send the formatted weather info back to Telegram
        await update.message.reply_text(response)
        
    except Exception as e:
        await update.message.reply_text(f"Error: Something went wrong: {e}")

def main():
    """Starts the Telegram bot."""
    print("Starting bot...")
    
    # Create bot application
    application = Application.builder().token(TOKEN).build()

    # Register command handler
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("weather", weather_command))

    print("Bot is running. Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == "__main__":
    main()