#!/usr/bin/env python3
"""
KSP VIP VPN Bot - Complete Auto System
"""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import json
from database import create_request, approve_request, cut_credits, add_vip, get, set
import time

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

print("=" * 60)
print("🤖 KSP VIP VPN BOT - AUTO SYSTEM")
print("=" * 60)

# Load config
with open("config.json") as f:
    config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]
ADMIN_ID = config["ADMIN_ID"]

# VIP Packages
VIP_PACKAGES = {
    "1month": {"days": 30, "price": 50, "name": "1 Month VIP"},
    "2month": {"days": 60, "price": 100, "name": "2 Months VIP"},
    "3month": {"days": 90, "price": 120, "name": "3 Months VIP"},
    "6month": {"days": 180, "price": 200, "name": "6 Months VIP"}
}

# Credit Packages
CREDIT_PACKAGES = {
    "50credits": {"credits": 50, "price_usd": 1, "name": "50 Credits"},
    "100credits": {"credits": 100, "price_usd": 2, "name": "100 Credits"},
    "200credits": {"credits": 200, "price_usd": 3.5, "name": "200 Credits"},
    "500credits": {"credits": 500, "price_usd": 8, "name": "500 Credits"}
}

# ========================
# KEYBOARDS
# ========================
def main_menu_keyboard():
    """Main menu inline keyboard"""
    keyboard = [
        [InlineKeyboardButton("💰 Buy Credits", callback_data='menu_credits')],
        [InlineKeyboardButton("👑 VIP Packages", callback_data='menu_vip')],
        [InlineKeyboardButton("🔑 Submit Token", callback_data='menu_token')],
        [InlineKeyboardButton("📊 My Balance", callback_data='menu_balance')],
        [InlineKeyboardButton("🆘 Help", callback_data='menu_help')]
    ]
    return InlineKeyboardMarkup(keyboard)

def credits_menu_keyboard():
    """Credits purchase menu"""
    keyboard = [
        [
            InlineKeyboardButton("50 Credits - $1", callback_data='buy_50credits'),
            InlineKeyboardButton("100 Credits - $2", callback_data='buy_100credits')
        ],
        [
            InlineKeyboardButton("200 Credits - $3.5", callback_data='buy_200credits'),
            InlineKeyboardButton("500 Credits - $8", callback_data='buy_500credits')
        ],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='menu_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def vip_menu_keyboard():
    """VIP packages menu"""
    keyboard = [
        [
            InlineKeyboardButton("1 Month - 50 credits", callback_data='vip_1month'),
            InlineKeyboardButton("2 Months - 100 credits", callback_data='vip_2month')
        ],
        [
            InlineKeyboardButton("3 Months - 120 credits", callback_data='vip_3month'),
            InlineKeyboardButton("6 Months - 200 credits", callback_data='vip_6month')
        ],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='menu_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def payment_method_keyboard(package_type, package_id):
    """Payment method selection"""
    keyboard = [
        [InlineKeyboardButton("💳 Credit/Debit Card", callback_data=f'pay_card_{package_type}_{package_id}')],
        [InlineKeyboardButton("📲 Mobile Payment", callback_data=f'pay_mobile_{package_type}_{package_id}')],
        [InlineKeyboardButton("🔙 Back", callback_data=f'menu_{package_type}')]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========================
# COMMAND HANDLERS
# ========================
def start(update: Update, context: CallbackContext):
    """Handle /start command with menu"""
    user = update.effective_user
    print(f"📱 /start from {user.id} ({user.first_name})")
    
    welcome_msg = (
        f"✨ *Welcome to KSP VIP VPN Bot!*\n\n"
        f"👤 *User:* {user.first_name}\n"
        f"🆔 *ID:* `{user.id}`\n\n"
        f"*Premium VPN Services:*\n"
        f"✅ Ultra Fast Speed\n"
        f"✅ Unlimited Bandwidth\n"
        f"✅ No Logs Policy\n"
        f"✅ 24/7 Support\n\n"
        f"👇 *Use the menu below to get started:*"
    )
    
    update.message.reply_text(
        welcome_msg,
        parse_mode='Markdown',
        reply_markup=main_menu_keyboard()
    )

def help_command(update: Update, context: CallbackContext):
    """Handle /help command"""
    help_text = (
        "🆘 *KSP VIP VPN Bot Help*\n\n"
        "*How to Use:*\n"
        "1. *Buy Credits* → Purchase credits\n"
        "2. *VIP Packages* → Activate VIP access\n"
        "3. *Submit Token* → Earn credits by submitting tokens\n\n"
        "*Payment Methods:*\n"
        "• Credit/Debit Cards\n"
        "• Mobile Payments\n\n"
        "*Support:* @KSPAdmin"
    )
    
    update.message.reply_text(help_text, parse_mode='Markdown')

# ========================
# CALLBACK QUERY HANDLERS
# ========================
def button_callback(update: Update, context: CallbackContext):
    """Handle button callbacks"""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    print(f"🔘 Button pressed: {data} by {user_id}")
    
    # Edit message based on callback data
    if data == 'menu_main':
        query.edit_message_text(
            "🏠 *Main Menu*\n\nSelect an option:",
            parse_mode='Markdown',
            reply_markup=main_menu_keyboard()
        )
    
    elif data == 'menu_credits':
        query.edit_message_text(
            "💰 *Buy Credits*\n\nSelect a credit package:",
            parse_mode='Markdown',
            reply_markup=credits_menu_keyboard()
        )
    
    elif data == 'menu_vip':
        query.edit_message_text(
            "👑 *VIP Packages*\n\nSelect VIP package:",
            parse_mode='Markdown',
            reply_markup=vip_menu_keyboard()
        )
    
    elif data == 'menu_balance':
        # Check user balance
        user_data = get(f"users/{user_id}") or {}
        credits = user_data.get("credits", 0)
        vip_status = "✅ Active" if user_data.get("vip") else "❌ Inactive"
        
        balance_msg = (
            f"📊 *Your Account Balance*\n\n"
            f"👤 *User:* {query.from_user.first_name}\n"
            f"🆔 *ID:* `{user_id}`\n"
            f"💎 *Credits:* {credits}\n"
            f"👑 *VIP Status:* {vip_status}\n\n"
            f"*Options:*"
        )
        
        keyboard = [
            [InlineKeyboardButton("💰 Buy More Credits", callback_data='menu_credits')],
            [InlineKeyboardButton("👑 Activate VIP", callback_data='menu_vip')],
            [InlineKeyboardButton("🔙 Main Menu", callback_data='menu_main')]
        ]
        
        query.edit_message_text(
            balance_msg,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data.startswith('buy_'):
        # Credit purchase flow
        package_id = data.replace('buy_', '')
        package = CREDIT_PACKAGES.get(package_id)
        
        if package:
            package_msg = (
                f"🛒 *Purchase Confirmation*\n\n"
                f"📦 *Package:* {package['name']}\n"
                f"💎 *Credits:* {package['credits']}\n"
                f"💰 *Price:* ${package['price_usd']}\n\n"
                f"Select payment method:"
            )
            
            query.edit_message_text(
                package_msg,
                parse_mode='Markdown',
                reply_markup=payment_method_keyboard('credits', package_id)
            )
    
    elif data.startswith('vip_'):
        # VIP purchase flow
        package_id = data.replace('vip_', '')
        package = VIP_PACKAGES.get(package_id)
        
        if package:
            # Check if user has enough credits
            user_data = get(f"users/{user_id}") or {}
            user_credits = user_data.get("credits", 0)
            
            if user_credits >= package['price']:
                package_msg = (
                    f"👑 *VIP Activation*\n\n"
                    f"📦 *Package:* {package['name']}\n"
                    f"📅 *Duration:* {package['days']} days\n"
                    f"💎 *Cost:* {package['price']} credits\n"
                    f"💳 *Your Credits:* {user_credits}\n\n"
                    f"✅ *Status:* Sufficient credits\n\n"
                    f"Click below to activate:"
                )
                
                keyboard = [
                    [InlineKeyboardButton(f"✅ Activate {package['name']}", callback_data=f'confirm_vip_{package_id}')],
                    [InlineKeyboardButton("🔙 Back", callback_data='menu_vip')]
                ]
                
            else:
                package_msg = (
                    f"👑 *VIP Activation*\n\n"
                    f"📦 *Package:* {package['name']}\n"
                    f"📅 *Duration:* {package['days']} days\n"
                    f"💎 *Cost:* {package['price']} credits\n"
                    f"💳 *Your Credits:* {user_credits}\n\n"
                    f"❌ *Status:* Insufficient credits\n\n"
                    f"You need {package['price'] - user_credits} more credits."
                )
                
                keyboard = [
                    [InlineKeyboardButton("💰 Buy Credits", callback_data='menu_credits')],
                    [InlineKeyboardButton("🔙 Back", callback_data='menu_vip')]
                ]
            
            query.edit_message_text(
                package_msg,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    elif data.startswith('confirm_vip_'):
        # Confirm VIP activation
        package_id = data.replace('confirm_vip_', '')
        package = VIP_PACKAGES.get(package_id)
        
        if package:
            # Deduct credits and activate VIP
            user_data = get(f"users/{user_id}") or {}
            user_credits = user_data.get("credits", 0)
            
            if user_credits >= package['price']:
                # Deduct credits
                new_credits = user_credits - package['price']
                set(f"users/{user_id}", {"credits": new_credits})
                
                # Add VIP
                expiry = add_vip(user_id, package['days'])
                
                success_msg = (
                    f"🎉 *VIP Activated Successfully!*\n\n"
                    f"📦 *Package:* {package['name']}\n"
                    f"📅 *Duration:* {package['days']} days\n"
                    f"💎 *Credits Used:* {package['price']}\n"
                    f"💳 *Remaining Credits:* {new_credits}\n"
                    f"✅ *Status:* Active\n\n"
                    f"Thank you for choosing KSP VIP VPN!"
                )
                
                query.edit_message_text(
                    success_msg,
                    parse_mode='Markdown'
                )
                
                # Send VIP details in a separate message
                expiry_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expiry))
                details_msg = (
                    f"📋 *VIP Details*\n\n"
                    f"👤 *User:* {query.from_user.first_name}\n"
                    f"🆔 *ID:* `{user_id}`\n"
                    f"📦 *Package:* {package['name']}\n"
                    f"⏰ *Expiry:* {expiry_date}\n\n"
                    f"*Enjoy premium VPN service!*"
                )
                
                context.bot.send_message(
                    chat_id=user_id,
                    text=details_msg,
                    parse_mode='Markdown'
                )
                
            else:
                query.edit_message_text(
                    "❌ *Insufficient Credits*\n\nPlease buy more credits first.",
                    parse_mode='Markdown'
                )
    
    elif data == 'menu_token':
        # Token submission menu
        token_msg = (
            f"🔑 *Submit Token*\n\n"
            f"*Earn credits by submitting VPN tokens!*\n\n"
            f"*How it works:*\n"
            f"1. Submit your VPN token\n"
            f"2. Admin reviews and approves\n"
            f"3. Get credits instantly\n\n"
            f"*Command:* `/token YOUR_TOKEN DAYS PRICE`\n\n"
            f"*Example:*\n"
            f"`/token abc123xyz 30 1000`"
        )
        
        keyboard = [
            [InlineKeyboardButton("📝 Submit Now", switch_inline_query_current_chat="/token ")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data='menu_main')]
        ]
        
        query.edit_message_text(
            token_msg,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == 'menu_help':
        help_command(update, context)
        query.answer()

# ========================
# TEXT COMMAND HANDLERS
# ========================
def token_command(update: Update, context: CallbackContext):
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
        
        # Notify admin
        admin_msg = (
            f"🔔 *New Token Submission*\n\n"
            f"👤 *User:* {update.effective_user.first_name}\n"
            f"🆔 *User ID:* `{user_id}`\n"
            f"📌 *Request ID:* `{req_id}`\n"
            f"📅 *Days:* {days}\n"
            f"💰 *Price:* {price} credits\n\n"
            f"*Approve with:* `/approve {req_id}`"
        )
        
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_msg,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        update.message.reply_text(f"❌ *Error:* {str(e)}", parse_mode='Markdown')

def approve_command(update: Update, context: CallbackContext):
    """Handle /approve command"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        update.message.reply_text("❌ *Admin only command*", parse_mode='Markdown')
        return
    
    if len(context.args) < 1:
        update.message.reply_text("📝 *Usage:* `/approve REQUEST_ID`", parse_mode='Markdown')
        return
    
    req_id = context.args[0]
    result = approve_request(req_id)
    
    if result == "approved":
        update.message.reply_text(f"✅ *Request {req_id} approved!*", parse_mode='Markdown')
    else:
        update.message.reply_text(f"❌ *Result:* {result}", parse_mode='Markdown')

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
        dp.add_handler(CommandHandler("help", help_command))
        dp.add_handler(CommandHandler("token", token_command))
        dp.add_handler(CommandHandler("approve", approve_command))
        
        # Callback query handler
        dp.add_handler(CallbackQueryHandler(button_callback))
        
        print("✅ Bot setup complete")
        print("🔄 Starting polling...")
        
        updater.start_polling()
        
        print("\n" + "=" * 60)
        print("🎉 KSP VIP VPN AUTO SYSTEM IS LIVE!")
        print("=" * 60)
        print("✨ Features:")
        print("  • Inline Menu System")
        print("  • Credit Purchase")
        print("  • VIP Package Activation")
        print("  • Token Submission")
        print("  • Auto Payment Processing")
        print("  • Admin Dashboard")
        print("=" * 60)
        
        updater.idle()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
