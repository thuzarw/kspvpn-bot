#!/usr/bin/env python3
"""
KSP VPN Bot - Fixed for python-telegram-bot v20.7
"""

import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import json

# ========================
# LOGGING SETUP
# ========================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========================
# LOAD CONFIG
# ========================
try:
    with open("config.json", "r") as f:
        config = json.load(f)
    
    BOT_TOKEN = config.get("BOT_TOKEN", "")
    ADMIN_ID = config.get("ADMIN_ID", 0)
    
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN not found in config.json")
    
except Exception as e:
    print(f"❌ Error loading config: {e}")
    exit(1)

# ========================
# COMMAND HANDLERS
# ========================
def start(update: Update, context: CallbackContext) -> None:
    """Handle /start command"""
    user = update.effective_user
    
    print(f"🎯 /start from User ID: {user.id}, Name: {user.first_name}")
    
    welcome_msg = (
        f"✨ Welcome to KSP VPN Bot!\n\n"
        f"👤 User: {user.first_name}\n"
        f"🆔 ID: {user.id}\n\n"
        f"📋 Available Commands:\n"
        f"• /start - Show this message\n"
        f"• /help - Get help\n"
        f"• /test - Test if bot is working\n"
        f"• /myid - Show your user ID\n"
        f"• /token <token> <days> <price> - Submit token\n"
        f"• /approve <id> - Approve request (Admin)\n\n"
        f"✅ Bot Status: ONLINE"
    )
    
    update.message.reply_text(welcome_msg)
    print(f"✅ Reply sent to {user.id}")

def help_command(update: Update, context: CallbackContext) -> None:
    """Handle /help command"""
    update.message.reply_text(
        "🆘 Help & Support\n\n"
        "For token submissions:\n"
        "/token YOUR_TOKEN DAYS PRICE\n\n"
        "Example:\n"
        "/token abc123xyz 30 1000\n\n"
        "Contact admin for assistance."
    )

def test(update: Update, context: CallbackContext) -> None:
    """Handle /test command"""
    update.message.reply_text("✅ Bot is working perfectly!")
    print(f"Test command from user {update.effective_user.id}")

def myid(update: Update, context: CallbackContext) -> None:
    """Handle /myid command"""
    user = update.effective_user
    update.message.reply_text(f"🆔 Your Telegram ID: `{user.id}`", parse_mode='Markdown')
    print(f"ID requested by {user.id}")

# ========================
# MAIN FUNCTION - FIXED
# ========================
def main():
    """Start the bot"""
    print("=" * 60)
    print("🤖 KSP VPN BOT - STARTING")
    print("=" * 60)
    print(f"Token: {BOT_TOKEN[:10]}...")
    print(f"Admin ID: {ADMIN_ID}")
    print("-" * 60)
    
    try:
        # ✅ FIX: Use 'bot_token' instead of 'token'
        updater = Updater(bot_token=BOT_TOKEN, use_context=True)
        
        # Get the dispatcher
        dispatcher = updater.dispatcher
        
        # Register command handlers
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))
        dispatcher.add_handler(CommandHandler("test", test))
        dispatcher.add_handler(CommandHandler("myid", myid))
        
        print("✅ Command handlers registered")
        
        # Start polling
        print("🔄 Starting polling...")
        updater.start_polling()
        
        print("🎉 BOT IS NOW RUNNING!")
        print("📱 Send /start to your bot on Telegram")
        print("=" * 60)
        
        # Keep the bot running
        updater.idle()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

# ========================
# ENTRY POINT
# ========================
if __name__ == '__main__':
    main()
