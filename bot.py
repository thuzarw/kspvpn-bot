#!/usr/bin/env python3
"""
KSP VPN Bot - Version 13.15 Compatible
"""

import logging
from telegram.ext import Updater, CommandHandler
import json

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

print("=" * 50)
print("🤖 KSP VPN BOT - VERSION 13.15")
print("=" * 50)

# Load config
with open("config.json") as f:
    config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]
ADMIN_ID = config["ADMIN_ID"]

print(f"Token: {BOT_TOKEN[:10]}...")
print(f"Admin ID: {ADMIN_ID}")

# Command handlers
def start(update, context):
    """Handle /start command"""
    user = update.effective_user
    print(f"📱 /start from {user.id} ({user.first_name})")
    
    message = (
        f"🎉 Welcome {user.first_name}!\n"
        f"🆔 Your ID: {user.id}\n\n"
        f"📋 Available Commands:\n"
        f"/start - Show this message\n"
        f"/help - Get help\n"
        f"/test - Test bot\n"
        f"/myid - Show your ID\n"
        f"/token <token> <days> <price> - Submit token\n"
        f"/approve <req_id> - Approve request (Admin only)\n\n"
        f"✅ Bot Status: ONLINE"
    )
    
    update.message.reply_text(message)

def help_command(update, context):
    """Handle /help command"""
    update.message.reply_text(
        "ℹ️ Help & Support\n\n"
        "For token submission:\n"
        "/token YOUR_TOKEN DAYS PRICE\n\n"
        "Example:\n"
        "/token abc123xyz 30 1000"
    )

def test(update, context):
    """Handle /test command"""
    update.message.reply_text("✅ Bot is working perfectly!")

def myid(update, context):
    """Handle /myid command"""
    user = update.effective_user
    update.message.reply_text(f"🆔 Your Telegram ID: `{user.id}`", parse_mode='Markdown')

def token_request(update, context):
    """Handle /token command"""
    if len(context.args) < 3:
        update.message.reply_text(
            "Usage: /token <token> <days> <price>\n"
            "Example: /token abc123xyz 30 1000"
        )
        return
    
    try:
        token = context.args[0]
        days = int(context.args[1])
        price = int(context.args[2])
        
        update.message.reply_text(
            f"✅ Token submitted!\n"
            f"📝 Token: {token[:10]}...\n"
            f"📅 Days: {days}\n"
            f"💰 Price: {price}\n\n"
            f"⏳ Waiting for admin approval..."
        )
        
        print(f"📝 Token request: User={update.effective_user.id}, Token={token}, Days={days}, Price={price}")
        
    except Exception as e:
        update.message.reply_text(f"❌ Error: {e}")

def approve(update, context):
    """Handle /approve command (Admin only)"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        update.message.reply_text("❌ Admin only command")
        return
    
    if len(context.args) < 1:
        update.message.reply_text("Usage: /approve <request_id>")
        return
    
    req_id = context.args[0]
    update.message.reply_text(f"✅ Request {req_id} approved!")
    print(f"👑 Admin approved request: {req_id}")

def main():
    """Start the bot"""
    try:
        # Create Updater - VERSION 13.15 SYNTAX
        updater = Updater(BOT_TOKEN, use_context=True)
        
        # Get dispatcher
        dp = updater.dispatcher
        
        # Add command handlers
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help_command))
        dp.add_handler(CommandHandler("test", test))
        dp.add_handler(CommandHandler("myid", myid))
        dp.add_handler(CommandHandler("token", token_request))
        dp.add_handler(CommandHandler("approve", approve))
        
        print("✅ Command handlers registered")
        print("🔄 Starting polling...")
        
        # Start polling
        updater.start_polling()
        
        print("🎉 BOT IS NOW RUNNING!")
        print("📱 Send /start to your bot")
        print("=" * 50)
        
        # Keep bot running
        updater.idle()
        
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
