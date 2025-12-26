#!/usr/bin/env python3
"""
KSP VPN Bot - Complete Working System
"""

import logging
from telegram.ext import Updater, CommandHandler
import json
from database import create_request, approve_request, cut_credits, add_vip

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

print("=" * 60)
print("🤖 KSP VPN BOT - COMPLETE SYSTEM")
print("=" * 60)

# Load config
with open("config.json") as f:
    config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]
ADMIN_ID = config["ADMIN_ID"]

print(f"Token: {BOT_TOKEN[:15]}...")
print(f"Admin ID: {ADMIN_ID}")
print(f"Firebase DB: {config['FIREBASE_DB'][:30]}...")

# ========================
# COMMAND HANDLERS
# ========================
def start(update, context):
    """Handle /start command"""
    user = update.effective_user
    print(f"📱 /start from {user.id} ({user.first_name})")
    
    message = (
        f"✨ *Welcome to KSP VPN Bot!*\n\n"
        f"👤 *User:* {user.first_name}\n"
        f"🆔 *ID:* `{user.id}`\n\n"
        f"📋 *Available Commands:*\n"
        f"• /start - Show this message\n"
        f"• /help - Get help\n"
        f"• /test - Test bot\n"
        f"• /myid - Show your ID\n"
        f"• /balance - Check credits\n"
        f"• /token <token> <days> <price> - Submit token\n"
        f"• /approve <req_id> - Approve request (Admin)\n\n"
        f"✅ *Status:* ONLINE"
    )
    
    update.message.reply_text(message, parse_mode='Markdown')

def help_command(update, context):
    """Handle /help command"""
    update.message.reply_text(
        "🆘 *Help & Support*\n\n"
        "📝 *Token Submission:*\n"
        "`/token TOKEN DAYS PRICE`\n\n"
        "📋 *Example:*\n"
        "`/token abc123xyz 30 1000`\n\n"
        "💰 *Credits System:*\n"
        "• Submit tokens to earn credits\n"
        "• Use credits to get VIP access\n\n"
        "👑 *Admin Commands:*\n"
        "`/approve REQUEST_ID`",
        parse_mode='Markdown'
    )

def test(update, context):
    """Test command"""
    update.message.reply_text("✅ *Bot is working perfectly!*", parse_mode='Markdown')
    print(f"Test command from {update.effective_user.id}")

def myid(update, context):
    """Show user ID"""
    user = update.effective_user
    update.message.reply_text(f"🆔 *Your Telegram ID:* `{user.id}`", parse_mode='Markdown')

def token(update, context):
    """Handle /token command"""
    user_id = update.effective_user.id
    
    if len(context.args) < 3:
        update.message.reply_text(
            "📝 *Usage:* `/token TOKEN DAYS PRICE`\n\n"
            "📋 *Example:*\n"
            "`/token abc123xyz 30 1000`",
            parse_mode='Markdown'
        )
        return
    
    try:
        token_str = context.args[0]
        days = int(context.args[1])
        price = int(context.args[2])
        
        # Validate
        if days <= 0 or price <= 0:
            update.message.reply_text("❌ Days and price must be positive numbers")
            return
        
        # Save to database
        req_id = create_request(user_id, token_str, days, price)
        
        update.message.reply_text(
            f"✅ *Token Submitted Successfully!*\n\n"
            f"📌 *Request ID:* `{req_id}`\n"
            f"🔑 *Token:* `{token_str[:10]}...`\n"
            f"📅 *Days:* {days}\n"
            f"💰 *Price:* {price} credits\n\n"
            f"⏳ *Status:* Waiting for admin approval\n"
            f"👑 *Admin:* Use `/approve {req_id}`",
            parse_mode='Markdown'
        )
        
        print(f"📝 Token request: User={user_id}, ReqID={req_id}, Days={days}, Price={price}")
        
    except ValueError:
        update.message.reply_text("❌ Invalid number format for days or price")
    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")
        print(f"❌ Token error: {e}")

def approve(update, context):
    """Handle /approve command (Admin only)"""
    user_id = update.effective_user.id
    
    # Check if admin
    if user_id != ADMIN_ID:
        update.message.reply_text("❌ *Admin only command*", parse_mode='Markdown')
        return
    
    if len(context.args) < 1:
        update.message.reply_text("📝 *Usage:* `/approve REQUEST_ID`", parse_mode='Markdown')
        return
    
    req_id = context.args[0]
    
    try:
        # Approve in database
        result = approve_request(req_id)
        
        if result == "approved":
            update.message.reply_text(
                f"✅ *Request Approved!*\n"
                f"📌 *Request ID:* `{req_id}`\n"
                f"✅ *Status:* Approved successfully",
                parse_mode='Markdown'
            )
            print(f"👑 Admin approved: {req_id}")
            
        elif result == "no_credit":
            update.message.reply_text(
                f"❌ *Approval Failed*\n"
                f"📌 *Request ID:* `{req_id}`\n"
                f"❌ *Reason:* Insufficient credits",
                parse_mode='Markdown'
            )
            
        elif result == "not_found":
            update.message.reply_text(
                f"❌ *Request Not Found*\n"
                f"📌 *Request ID:* `{req_id}`",
                parse_mode='Markdown'
            )
            
        elif result == "already_processed":
            update.message.reply_text(
                f"⚠️ *Already Processed*\n"
                f"📌 *Request ID:* `{req_id}`",
                parse_mode='Markdown'
            )
            
        else:
            update.message.reply_text(f"⚠️ *Result:* {result}", parse_mode='Markdown')
            
    except Exception as e:
        update.message.reply_text(f"❌ *Approval error:* {str(e)}", parse_mode='Markdown')
        print(f"❌ Approval error: {e}")

def balance(update, context):
    """Check user credits balance"""
    user_id = update.effective_user.id
    
    try:
        from database import get
        user_data = get(f"users/{user_id}") or {}
        credits = user_data.get("credits", 0)
        
        update.message.reply_text(
            f"💰 *Your Balance*\n\n"
            f"👤 *User:* {update.effective_user.first_name}\n"
            f"🆔 *ID:* `{user_id}`\n"
            f"💎 *Credits:* {credits}\n\n"
            f"📝 *Earn credits by submitting tokens!*",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        update.message.reply_text(f"❌ Error checking balance: {str(e)}")
        print(f"❌ Balance error: {e}")

# ========================
# MAIN FUNCTION
# ========================
def main():
    """Start the bot"""
    try:
        # Create Updater
        updater = Updater(BOT_TOKEN, use_context=True)
        
        # Get dispatcher
        dp = updater.dispatcher
        
        # Add command handlers
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", help_command))
        dp.add_handler(CommandHandler("test", test))
        dp.add_handler(CommandHandler("myid", myid))
        dp.add_handler(CommandHandler("token", token))
        dp.add_handler(CommandHandler("approve", approve))
        dp.add_handler(CommandHandler("balance", balance))
        
        print("✅ All command handlers registered")
        print("🔄 Starting polling...")
        
        # Start polling
        updater.start_polling()
        
        print("\n" + "=" * 60)
        print("🎉 KSP VPN BOT SYSTEM IS LIVE!")
        print("=" * 60)
        print("📱 Available Commands:")
        print("  /start     - Welcome message")
        print("  /help      - Get help")
        print("  /test      - Test bot")
        print("  /myid      - Show your ID")
        print("  /balance   - Check credits")
        print("  /token     - Submit token request")
        print("  /approve   - Approve request (Admin)")
        print("=" * 60)
        print("⚡ Bot is ready to process requests!")
        print("=" * 60)
        
        # Keep bot running
        updater.idle()
        
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
