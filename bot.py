import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import json
from queue import Queue

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
    """Handle /start command"""
    user = update.effective_user
    
    # Log to terminal
    print(f"✅ /start received from: {user.id} - {user.first_name}")
    
    reply_text = (
        f'🎉 Welcome {user.first_name}!\n'
        f'🆔 Your ID: {user.id}\n\n'
        f'📋 Available Commands:\n'
        f'/start - Show this message\n'
        f'/help - Show help\n'
        f'/test - Test command\n'
        f'/token <token> <days> <price> - Submit token request\n'
        f'/approve <req_id> - Approve request (Admin only)'
    )
    
    update.message.reply_text(reply_text)
    print(f"📤 Reply sent to user {user.id}")

def help_command(update: Update, context: CallbackContext) -> None:
    """Handle /help command"""
    update.message.reply_text('ℹ️ Help: Use /start to see available commands')

def test(update: Update, context: CallbackContext) -> None:
    """Test command"""
    update.message.reply_text('✅ Bot is working perfectly!')

def main() -> None:
    """Start the bot"""
    print("=" * 50)
    print("🤖 KSP VPN BOT STARTING...")
    print(f"🔑 Token: {BOT_TOKEN[:15]}...")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print("=" * 50)
    
    try:
        # Create update queue
        update_queue = Queue()
        
        # Create Updater with the queue
        updater = Updater(
            token=BOT_TOKEN,
            update_queue=update_queue,
            use_context=True
        )
        
        # Get dispatcher
        dispatcher = updater.dispatcher
        
        # Add command handlers
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))
        dispatcher.add_handler(CommandHandler("test", test))
        
        print("✅ Command handlers registered")
        
        # Start the bot
        print("🔄 Starting polling...")
        updater.start_polling()
        
        print("🎉 Bot is now running!")
        print("📱 Send /start to your bot on Telegram")
        print("⏳ Waiting for messages...")
        print("=" * 50)
        
        # Run the bot until Ctrl+C
        updater.idle()
        
    except Exception as e:
        print(f"❌ ERROR starting bot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
