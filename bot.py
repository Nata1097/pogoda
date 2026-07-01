import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from weather_api import get_current_weather
from db import save_weather_to_db

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Define Conversation States
OUTFIT, FEELING, ACTIVITY_COMMENT = range(3)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a friendly welcome message when the user types /start."""
    await update.message.reply_text(
        "Hi! I am your Weather and Outfit Assistant.\n"
        "Type /weather to see the current conditions.\n"
        "Type /log to start recording your outfit and comfort level!"
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
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"Error: Something went wrong: {e}")

# --- CONVERSATION HANDLER LOGIC ---

async def log_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the log conversation and asks for the outfit."""
    await update.message.reply_text(
        "Let's log your outfit!\n"
        "Please enter what you wore in the following format (separated by commas):\n"
        "Top, Bottom, Jacket, Accessories\n\n"
        "Example: t-shirt, jeans, none, sunglasses"
    )
    return OUTFIT

async def log_outfit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stores the outfit data and asks about the thermal feeling using buttons."""
    user_text = update.message.text
    parts = [p.strip() for p in user_text.split(",")]
    
    # If the user did not provide all 4 parts, we pad it with "none"
    while len(parts) < 4:
        parts.append("none")
        
    # Store data temporarily in context.user_data
    context.user_data["clothing_top"] = parts[0]
    context.user_data["clothing_bottom"] = parts[1]
    context.user_data["clothing_jacket"] = parts[2]
    context.user_data["clothing_accessories"] = parts[3]
    
    # Create buttons for the user to click
    keyboard = [
        [InlineKeyboardButton("Too cold", callback_data="Too cold")],
        [InlineKeyboardButton("Perfect", callback_data="Perfect")],
        [InlineKeyboardButton("Too hot", callback_data="Too hot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "How did you feel in this outfit?",
        reply_markup=reply_markup
    )
    return FEELING

async def log_feeling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stores the thermal feeling and asks for activity and comments."""
    query = update.callback_query
    await query.answer()
    
    # Store the button choice
    context.user_data["feeling"] = query.data
    
    # Edit message to confirm choice and ask the next question
    await query.edit_message_text(
        f"Feeling saved: {query.data}\n\n"
        "Now, please type your activity and any extra comments.\n"
        "Example: Dog walking with Bilbo, very windy"
    )
    return ACTIVITY_COMMENT

async def log_activity_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetches weather, merges all data, saves to DB, and ends the conversation."""
    user_text = update.message.text
    
    # Simple split into activity and comment if comma exists, else put everything in activity
    if "," in user_text:
        activity, comment = user_text.split(",", 1)
        context.user_data["activity"] = activity.strip()
        context.user_data["comment"] = comment.strip()
    else:
        context.user_data["activity"] = user_text.strip()
        context.user_data["comment"] = "none"
        
    await update.message.reply_text("Fetching current weather and saving your log... Please wait.")
    
    try:
        # 1. Fetch current weather from Open-Meteo
        weather = get_current_weather()
        
        # 2. Combine weather data with user data
        complete_log = {
            "timestamp": weather["timestamp"],
            "temperature": weather["temperature"],
            "apparent_temperature": weather["apparent_temperature"],
            "wind_speed": weather["wind_speed"],
            "clothing_top": context.user_data["clothing_top"],
            "clothing_bottom": context.user_data["clothing_bottom"],
            "clothing_jacket": context.user_data["clothing_jacket"],
            "clothing_accessories": context.user_data["clothing_accessories"],
            "feeling": context.user_data["feeling"],
            "activity": context.user_data["activity"],
            "comment": context.user_data["comment"]
        }
        
        # 3. Save to SQLite database using your db.py module
        save_weather_to_db(complete_log)
        
        # 4. Confirm to user
        await update.message.reply_text(
            "Success! Your log has been saved to the database.\n\n"
            f"Summary:\n"
            f"Temp: {complete_log['temperature']} C, Outfit: {complete_log['clothing_top']} + {complete_log['clothing_bottom']}\n"
            f"Feeling: {complete_log['feeling']}"
        )
        
    except Exception as e:
        await update.message.reply_text(f"Error while saving data: {e}")
        
    # Clear temporary session data and end conversation
    context.user_data.clear()
    return ConversationHandler.END

async def log_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels the conversation."""
    await update.message.reply_text("Logging cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

def main():
    """Starts the Telegram bot."""
    print("Starting bot...")
    application = Application.builder().token(TOKEN).build()

    # Create the ConversationHandler for /log
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("log", log_start)],
        states={
            OUTFIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, log_outfit)],
            FEELING: [CallbackQueryHandler(log_feeling)],
            ACTIVITY_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, log_activity_comment)],
        },
        fallbacks=[CommandHandler("cancel", log_cancel)],
    )

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(conv_handler)

    print("Bot is running. Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == "__main__":
    main()