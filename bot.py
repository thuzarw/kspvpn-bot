#!/usr/bin/env python3
"""
KSP VPN Bot - Working Version
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
print("🤖 KSP VPN BOT STARTING")
print("=" * 50)

# Load config
with open("config.json") as f:
    config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]
print(f"Token: {BOT_TOKEN[:10]}...")

# Command handlers
def start(update, context):
    user = update.effective_user
    print(f"📱 /start from {user.id} ({user.first_name})")
    
    msg = (
        f"🎉 Welcome {user.first_name}!\n"
        f"🆔 Your ID: {user.id}\n\n"
        f"✅ Bot is working!\n\n"
        f"Commands:\n"
        f"/start - Show this message\n"
        f"/help - Get help\n"
        f"/test - Test bot"
    )
    
    update.message.reply_text(msg)

def help_cmd(update, context):
    update.message.reply_text("ℹ️ Use /start to see commands")

def test(update, context):
    update.message.reply_text("✅ Bot test successful!")

def main():
    try:
        # ✅ SIMPLEST POSSIBLE - No extra parameters
        updater = Updater(BOT_TOKEN)
        
        dp = updater.dispatcher
        
        # Add handlers
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help_cmd))
        dp.add_handler(CommandHandler("test", test))
        
        print("✅ Handlers registered")
        print("🔄 Starting polling...")
        
        # Start polling
        updater.start_polling()
        
        print("🎉 BOT IS RUNNING!")
        print("📱 Send /start to @kspvpnvipbot")
        print("=" * 50)
        
        # Keep running
        updater.idle()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
