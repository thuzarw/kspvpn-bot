#!/usr/bin/env python3
"""
KSP VIP VPN Bot - Auto System with Inline Keyboard
"""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import json
from database import get_user, create_user, add_credits, cut_credits, add_vip

# Setup logging
logging.basicConfig(level=logging.INFO)

print("=" * 60)
print("🤖 KSP VIP VPN - INLINE MENU SYSTEM")
print("=" * 60)

# Load config
with open("config.json") as f:
    config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]
ADMIN_ID = config["ADMIN_ID"]

# VIP Packages
VIP_PACKAGES = {
    "1month": {"days": 30, "credits": 50, "name": "1 Month VIP"},
    "2month": {"days": 60, "credits": 100, "name": "2 Months VIP"},
    "3month": {"days": 90, "credits": 120, "name": "3 Months VIP"},
    "6month": {"days": 180, "credits": 200, "name": "6 Months VIP"}
}

# ========================
# KEYBOARDS
# ========================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("💰 Buy Credits", callback_data='credits')],
        [InlineKeyboardButton("👑 VIP Packages", callback_data='vip')],
        [InlineKeyboardButton("📊 My Balance", callback_data='balance')],
        [InlineKeyboardButton("🆘 Help", callback_data='help')]
    ]
    return InlineKeyboardMarkup(keyboard)

def credits_menu():
    keyboard = [
        [InlineKeyboardButton("50 Credits", callback_data='buy_50')],
        [InlineKeyboardButton("100 Credits", callback_data='buy_100')],
        [InlineKeyboardButton("200 Credits", callback_data='buy_200')],
        [InlineKeyboardButton("500 Credits", callback_data='buy_500')],
        [InlineKeyboardButton("🔙 Back", callback_data='back_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def vip_menu():
    keyboard = [
        [InlineKeyboardButton("1 Month - 50 credits", callback_data='vip_1')],
        [InlineKeyboardButton("2 Months - 100 credits", callback_data='vip_2')],
        [InlineKeyboardButton("3 Months - 120 credits", callback_data='vip_3')],
        [InlineKeyboardButton("6 Months - 200 credits", callback_data='vip_6')],
        [InlineKeyboardButton("🔙 Back", callback_data='back_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========================
# COMMAND HANDLERS
# ========================
def start(update, context):
    """Start command with inline keyboard"""
    user = update.effective_user
    user_id = user.id
    
    # Ensure user exists in database
    if not get_user(user_id):
        create_user(user_id, {"name": user.first_name})
    
    welcome = (
        f"✨ *Welcome to KSP VIP VPN!*\n\n"
        f"👤 *User:* {user.first_name}\n"
        f"🆔 *ID:* `{user_id}`\n\n"
        f"*Premium Features:*\n"
        f"✅ Ultra Fast Speed\n"
        f"✅ Unlimited Bandwidth\n"
        f"✅ No Logs Policy\n\n"
        f"👇 *Select an option below:*"
    )
    
    update.message.reply_text(
        welcome,
        parse_mode='Markdown',
        reply_markup=main_menu()
    )

def button_handler(update, context):
    """Handle inline keyboard button presses"""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    # Ensure user exists
    if not get_user(user_id):
        create_user(user_id, {"name": query.from_user.first_name})
    
    user_data = get_user(user_id) or {}
    credits = user_data.get('credits', 0)
    
    if data == 'credits':
        query.edit_message_text(
            "💰 *Buy Credits*\n\nSelect credit package:",
            parse_mode='Markdown',
            reply_markup=credits_menu()
        )
    
    elif data == 'vip':
        query.edit_message_text(
            "👑 *VIP Packages*\n\nSelect VIP package:",
            parse_mode='Markdown',
            reply_markup=vip_menu()
        )
    
    elif data == 'balance':
        vip_status = "✅ Active" if user_data.get('vip') else "❌ Inactive"
        query.edit_message_text(
            f"📊 *Your Balance*\n\n"
            f"💎 *Credits:* {credits}\n"
            f"👑 *VIP Status:* {vip_status}\n\n"
            f"*Options:*",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 Buy Credits", callback_data='credits')],
                [InlineKeyboardButton("👑 Get VIP", callback_data='vip')],
                [InlineKeyboardButton("🔙 Main Menu", callback_data='back_main')]
            ])
        )
    
    elif data.startswith('buy_'):
        amount = int(data.replace('buy_', ''))
        price_map = {50: 1, 100: 2, 200: 3.5, 500: 8}
        price = price_map.get(amount, 0)
        
        query.edit_message_text(
            f"🛒 *Purchase Details*\n\n"
            f"📦 *Package:* {amount} Credits\n"
            f"💰 *Price:* ${price}\n\n"
            f"*Payment Methods:*\n"
            f"• Credit/Debit Card\n"
            f"• Mobile Payment\n\n"
            f"*Contact admin for payment:* @KSPAdmin",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Pay Now", url=f"https://t.me/KSPAdmin")],
                [InlineKeyboardButton("🔙 Back", callback_data='credits')]
            ])
        )
    
    elif data.startswith('vip_'):
        vip_map = {'1': '1month', '2': '2month', '3': '3month', '6': '6month'}
        package_id = vip_map.get(data.replace('vip_', ''))
        package = VIP_PACKAGES.get(package_id)
        
        if package:
            if credits >= package['credits']:
                # Activate VIP
                add_vip(user_id, package['days'])
                cut_credits(user_id, package['credits'])
                
                new_credits = credits - package['credits']
                query.edit_message_text(
                    f"🎉 *VIP Activated!*\n\n"
                    f"📦 *Package:* {package['name']}\n"
                    f"📅 *Duration:* {package['days']} days\n"
                    f"💎 *Credits Used:* {package['credits']}\n"
                    f"💰 *Remaining:* {new_credits} credits\n\n"
                    f"✅ *Enjoy premium VPN access!*",
                    parse_mode='Markdown'
                )
            else:
                needed = package['credits'] - credits
                query.edit_message_text(
                    f"❌ *Insufficient Credits*\n\n"
                    f"📦 *Package:* {package['name']}\n"
                    f"💎 *Required:* {package['credits']} credits\n"
                    f"💰 *Your Balance:* {credits} credits\n"
                    f"📈 *Needed:* {needed} more credits\n\n"
                    f"*Please buy more credits first.*",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("💰 Buy Credits", callback_data='credits')],
                        [InlineKeyboardButton("🔙 Back", callback_data='vip')]
                    ])
                )
    
    elif data == 'help':
        query.edit_message_text(
            "🆘 *Help & Support*\n\n"
            "*How to Use:*\n"
            "1. *Buy Credits* → Purchase credits\n"
            "2. *VIP Packages* → Activate VIP access\n"
            "3. *My Balance* → Check your account\n\n"
            "*Need Help?*\n"
            "Contact: @KSPAdmin",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Main Menu", callback_data='back_main')]
            ])
        )
    
    elif data == 'back_main':
        query.edit_message_text(
            "🏠 *Main Menu*\n\nSelect an option:",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
    
    query.answer()

# ========================
# MAIN FUNCTION
# ========================
def main():
    """Start the bot"""
    try:
        updater = Updater(BOT_TOKEN, use_context=True)
        dp = updater.dispatcher
        
        # Command handlers
        dp.add_handler(CommandHandler("start", start))
        
        # Callback query handler for inline buttons
        dp.add_handler(CallbackQueryHandler(button_handler))
        
        print("✅ Bot setup complete")
        print("🔄 Starting polling...")
        
        updater.start_polling()
        
        print("\n" + "=" * 60)
        print("🎉 AUTO MENU BOT IS RUNNING!")
        print("=" * 60)
        print("✨ Features:")
        print("  • Inline Keyboard Menu")
        print("  • Credit Purchase System")
        print("  • VIP Activation")
        print("  • Balance Checking")
        print("  • Auto Database Management")
        print("=" * 60)
        print("📱 Send /start to test")
        print("=" * 60)
        
        updater.idle()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
