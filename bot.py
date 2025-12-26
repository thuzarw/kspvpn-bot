import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import json

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load config
with open("config.json") as f:
    config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]
ADMIN_ID = config["ADMIN_ID"]

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_text(
        f'🎉 Welcome {user.first_name}!\n'
        f'Your ID: {user.id}\n\n'
        f'📌 Available commands:\n'
        f'/start - Show this message\n'
        f'/help - Show help\n'
        f'/token <token> <days> <price> - Submit token'
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def main() -> None:
    """Start the bot."""
    print("🤖 Starting KSP VPN Bot...")
    
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Start the Bot
    print("🔄 Starting polling...")
    updater.start_polling()
    
    print("✅ Bot is running!")
    print("📱 Send /start to your bot on Telegram")
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
