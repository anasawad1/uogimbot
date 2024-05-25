from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
import logging

# Define the token for your bot
TOKEN = "6390533694:AAGqx-wucib5_rQQS06925pulqI4tTmdWIk"

# Define the main menu options
MAIN_MENU_OPTIONS = [
    "Obstetric",
    "Gynecology"
]

# Define a dictionary to store the chat IDs for each category and subcategory
CHAT_IDS = {
    "Obstetric_ExaminationVideos": "-4248783287",  # Replace with actual chat ID
    "Obstetric_NotesIllustrations": "-4223676816",  # Replace with actual chat ID
    "Gynecology_ExaminationVideos": "-4272787128",  # Replace with actual chat ID
    "Gynecology_NotesIllustrations": "-4269247757",  # Replace with actual chat ID
    # Add more as needed for other categories and subcategories
}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the start command handler
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    keyboard = [
        [InlineKeyboardButton(option, callback_data=option)] for option in MAIN_MENU_OPTIONS
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Welcome to the Obstetric & Gynecology bot! Please choose a category:", reply_markup=reply_markup)

# Define the submenu handler
def submenu(update: Update, context: CallbackContext) -> None:
    """Send a message when a submenu option is chosen."""
    query = update.callback_query
    query.answer()
    option = query.data
    if option in MAIN_MENU_OPTIONS:
        context.user_data["category"] = option
        keyboard = [
            [InlineKeyboardButton("Examination Videos", callback_data=f"{option}_ExaminationVideos")],
            [InlineKeyboardButton("Notes & Guidelines", callback_data=f"{option}_NotesIllustrations")],
            [InlineKeyboardButton("Back", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text(f"Please choose an option for {option}:", reply_markup=reply_markup)
    elif option.endswith("_ExaminationVideos") or option.endswith("_NotesIllustrations"):
        context.user_data["subcategory"] = option
        query.message.reply_text(f"Please upload your {option.split('_')[-1].lower().replace('videos', 'videos or files')}")

# Define the message handler to handle file uploads
def handle_files(update: Update, context: CallbackContext) -> None:
    """Handle file uploads and forward them to the appropriate chat."""
    file = update.message.document or update.message.video
    category = context.user_data.get("category")
    subcategory = context.user_data.get("subcategory")
    logging.info(f"Category: {category}, Subcategory: {subcategory}")
    if category and subcategory:
        key = f"{category}_{subcategory.split('_')[1]}"  # Remove the duplicate category name
        logging.info(f"Constructed key: {key}")
        chat_id = CHAT_IDS.get(key)
        logging.info(f"Chat ID: {chat_id}")
        if chat_id:
            try:
                if file.mime_type.startswith('video'):
                    context.bot.send_video(chat_id=chat_id, video=file.file_id)
                else:
                    context.bot.send_document(chat_id=chat_id, document=file.file_id)
                update.message.reply_text("Thanks for collaborating and making my life easier!")
            except Exception as e:
                logging.error(f"Error forwarding file: {e}")
                update.message.reply_text("An error occurred while forwarding the file. Please try again later.")
                return
            return
    update.message.reply_text("Sorry, something went wrong. Please try again later.")

# Define the get_chat_id command handler
def get_chat_id(update: Update, context: CallbackContext) -> None:
    """Get the chat ID of the current chat."""
    chat_id = update.message.chat_id
    update.message.reply_text(f"The chat ID is: {chat_id}")

# Define the main function
def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(submenu))
    dispatcher.add_handler(CommandHandler("get_chat_id", get_chat_id))

    # Message handler for file uploads
    dispatcher.add_handler(MessageHandler(Filters.document | Filters.video, handle_files))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM, or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
