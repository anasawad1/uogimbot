from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
import logging

# Define the token for your bot (replace 'YOUR_BOT_TOKEN' with the actual token)
TOKEN = "7151579267:AAEhwzmDNiv1FWCemKm7gHUhB4nWV4zhRpQ"

# Define the main menu options
MAIN_MENU_OPTIONS = [
    "CNS",
    "CVS",
    "GIT",
    "Pulmonary",
    "Endocrine",
    "Renal",
    "Dermatology",
    "Rheumatology"
]

# Define a dictionary to store the chat IDs for each category and subcategory
CHAT_IDS = {
    "CNS_ExaminationVideos": "-4287731629",
    "CNS_NotesIllustrations": "-4158965327",
    "CVS_ExaminationVideos": "-4283469380",
    "CVS_NotesIllustrations": "-4240317461",
    "GIT_ExaminationVideos": "-4239605671",
    "GIT_NotesIllustrations": "-4251428377",
    "Pulmonary_ExaminationVideos": "-4223331705",
    "Pulmonary_NotesIllustrations": "-4203487026",
    "Endocrine_ExaminationVideos": "-4212434090",
    "Endocrine_NotesIllustrations": "-4246032139",
    "Renal_ExaminationVideos": "-4234983411",
    "Renal_NotesIllustrations": "-4237135785",
    "Dermatology_ExaminationVideos": "-4261209338",
    "Dermatology_NotesIllustrations": "-4287520871",
    "Rheumatology_ExaminationVideos": "-4224206099",
    "Rheumatology_NotesIllustrations": "-4244991292",
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
    update.message.reply_text("Welcome to the Internal Medicine bot! Please choose a category:", reply_markup=reply_markup)

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

# Command to get the chat ID of the current chat
def get_chat_id(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    update.message.reply_text(f"Chat ID: {chat_id}")

# Define the main function
def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("get_chat_id", get_chat_id))  # Command to get the chat ID
    dispatcher.add_handler(CallbackQueryHandler(submenu))
    dispatcher.add_handler(MessageHandler(Filters.document | Filters.video, handle_files))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
