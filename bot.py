#!/usr/bin/env python3
"""
KSP VIP VPN - Complete Auto System
"""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import json
from database import (
    get_user, create_user, add_credits, cut_credits, add_vip,
    get_vip_status, add_payment_request, create_request, approve_request
)

# Setup
logging.basicConfig(level=logging.INFO)

print("=" * 60)
print("🤖 KSP VIP VPN - AUTO SYSTEM")
print("=" * 60)

with open("config.json") as f:
    config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]
ADMIN_ID = config["ADMIN_ID"]

# User states for conversation
user_states = {}

# ========================
# INLINE KEYBOARDS
# ========================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("💰 ငွေဖြည့်ရန်", callback_data='add_money')],
        [InlineKeyboardButton("👑 VIP ဝယ်ရန်", callback_data='buy_vip')],
        [InlineKeyboardButton("🔑 Token တင်ရန်", callback_data='submit_token')],
        [InlineKeyboardButton("📊 အကြွင်းစာရင်း", callback_data='check_balance')],
    ]
    return InlineKeyboardMarkup(keyboard)

def credit_packages_menu():
    keyboard = [
        [InlineKeyboardButton("50 Credits - 50ဘတ်", callback_data='credit_50')],
        [InlineKeyboardButton("100 Credits - 100ဘတ်", callback_data='credit_100')],
        [InlineKeyboardButton("200 Credits - 200ဘတ်", callback_data='credit_200')],
        [InlineKeyboardButton("500 Credits - 500ဘတ်", callback_data='credit_500')],
        [InlineKeyboardButton("🔙 နောက်သို့", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def vip_packages_menu():
    keyboard = [
        [InlineKeyboardButton("1 လ - 50 credits", callback_data='vip_1month')],
        [InlineKeyboardButton("2 လ - 100 credits", callback_data='vip_2month')],
        [InlineKeyboardButton("3 လ - 120 credits", callback_data='vip_3month')],
        [InlineKeyboardButton("6 လ - 200 credits", callback_data='vip_6month')],
        [InlineKeyboardButton("🔙 နောက်သို့", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========================
# COMMAND HANDLERS
# ========================
def start(update, context):
    """Start command"""
    user = update.effective_user
    user_id = user.id
    
    # Create user if not exists
    if not get_user(user_id):
        create_user(user_id, {
            "name": user.first_name,
            "username": user.username,
            "credits": 0,
            "vip": False
        })
    
    welcome_msg = (
        f"✨ *KSP VIP VPN မှကြိုဆိုပါတယ်* ✨\n\n"
        f"👤 အသုံးပြုသူ: {user.first_name}\n"
        f"🆔 အိုင်ဒီ: `{user_id}`\n\n"
        f"👇 *မီနူးကိုရွေးချယ်ပါ*"
    )
    
    update.message.reply_text(
        welcome_msg,
        parse_mode='Markdown',
        reply_markup=main_menu()
    )

# ========================
# BUTTON HANDLERS
# ========================
def button_handler(update, context):
    """Handle inline buttons"""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    # Ensure user exists
    if not get_user(user_id):
        create_user(user_id, {"name": query.from_user.first_name})
    
    user_data = get_user(user_id) or {}
    credits = user_data.get('credits', 0)
    
    if data == 'main_menu':
        query.edit_message_text(
            "🏠 *မူလမီနူး*\n\nရွေးချယ်ရန်:",
            parse_mode='Markdown',
            reply_markup=main_menu()
        )
    
    elif data == 'add_money':
        query.edit_message_text(
            "💰 *ငွေဖြည့်သွင်းရန်*\n\nပက်ကေ့ချ်ရွေးချယ်ပါ:",
            parse_mode='Markdown',
            reply_markup=credit_packages_menu()
        )
    
    elif data == 'buy_vip':
        vip_status = get_vip_status(user_id)
        
        if credits >= 50:
            message = (
                f"👑 *VIP ဝယ်ယူရန်*\n\n"
                f"💰 လက်ကျန်ငွေ: {credits} credits\n"
                f"✅ VIP ဝယ်ယူနိုင်ပါသည်\n\n"
                f"ပက်ကေ့ချ်ရွေးချယ်ပါ:"
            )
        else:
            needed = 50 - credits
            message = (
                f"👑 *VIP ဝယ်ယူရန်*\n\n"
                f"💰 လက်ကျန်ငွေ: {credits} credits\n"
                f"❌ VIP ဝယ်ယူရန် ငွေမလုံလောက်ပါ\n"
                f"📈 လိုအပ်ငွေ: {needed} credits\n\n"
                f"ငွေဖြည့်သွင်းရန် ကျေးဇူးပြု၍:"
            )
        
        query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=vip_packages_menu()
        )
    
    elif data == 'check_balance':
        vip_info = get_vip_status(user_id)
        vip_status = "✅ ဖွင့်ထားသည်" if vip_info.get('vip') else "❌ ပိတ်ထားသည်"
        
        query.edit_message_text(
            f"📊 *သင့်အကောင့်*\n\n"
            f"👤 အမည်: {query.from_user.first_name}\n"
            f"🆔 အိုင်ဒီ: `{user_id}`\n"
            f"💎 ခရက်ဒစ်: {credits}\n"
            f"👑 VIP အနေအထား: {vip_status}\n\n"
            f"*ရွေးချယ်ရန်:*",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 ငွေဖြည့်ရန်", callback_data='add_money')],
                [InlineKeyboardButton("👑 VIP ဝယ်ရန်", callback_data='buy_vip')],
                [InlineKeyboardButton("🔙 နောက်သို့", callback_data='main_menu')]
            ])
        )
    
    elif data == 'submit_token':
        # Set user state for token submission
        user_states[user_id] = 'waiting_for_token'
        
        query.edit_message_text(
            "🔑 *Token တင်သွင်းရန်*\n\n"
            "ကျေးဇူးပြု၍ အောက်ပါ format အတိုင်း token ပို့ပါ:\n\n"
            "`/token YOUR_TOKEN_HERE DAYS PRICE`\n\n"
            "📋 *ဥပမာ:*\n"
            "`/token ABC123XYZ 30 1000`\n\n"
            "📝 *ရှင်းလင်းချက်:*\n"
            "• YOUR_TOKEN_HERE = VPN Token\n"
            "• DAYS = ရက်ပေါင်း\n"
            "• PRICE = ခရက်ဒစ်ပမာဏ",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 နောက်သို့", callback_data='main_menu')]
            ])
        )
    
    elif data.startswith('credit_'):
        amounts = {'50': 50, '100': 100, '200': 200, '500': 500}
        amount = data.replace('credit_', '')
        credits_amount = amounts.get(amount, 50)
        price = credits_amount  # 50 credits = 50ဘတ်
        
        # Set user state for payment
        user_states[user_id] = f'payment_{amount}'
        
        kbpay_number = "09xxxxxxxxx"  # KBZ Pay number
        wave_number = "09xxxxxxxxx"   # Wave Money number
        
        query.edit_message_text(
            f"💰 *ငွေဖြည့်သွင်းရန်*\n\n"
            f"📦 ပက်ကေ့ချ်: {amount} Credits\n"
            f"💵 စျေးနှုန်း: {price} ဘတ်\n\n"
            f"*ငွေလွှဲရန်နံပါတ်များ:*\n"
            f"🏦 KBZ Pay: `{kbpay_number}`\n"
            f"📱 Wave Money: `{wave_number}`\n\n"
            f"*လုပ်ဆောင်ချက်:*\n"
            "1. ငွေလွှဲပြီးပါက\n"
            "2. ငွေလွှဲ Screenshot ပို့ပါ\n"
            "3. Admin မှအတည်ပြုပေးပါမည်\n\n"
            f"*မှတ်ချက်:* {amount} credits ရရှိမည်",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📸 Screenshot ပို့ရန်", callback_data='send_screenshot')],
                [InlineKeyboardButton("🔙 နောက်သို့", callback_data='add_money')]
            ])
        )
    
    elif data.startswith('vip_'):
        packages = {
            '1month': {"days": 30, "credits": 50, "name": "1 လ VIP"},
            '2month': {"days": 60, "credits": 100, "name": "2 လ VIP"},
            '3month': {"days": 90, "credits": 120, "name": "3 လ VIP"},
            '6month': {"days": 180, "credits": 200, "name": "6 လ VIP"}
        }
        
        package_id = data
        package = packages.get(package_id)
        
        if package:
            if credits >= package['credits']:
                # Activate VIP
                add_vip(user_id, package['days'])
                cut_credits(user_id, package['credits'])
                
                new_credits = credits - package['credits']
                
                query.edit_message_text(
                    f"🎉 *VIP အောင်မြင်စွာဖွင့်လိုက်ပါပြီ!*\n\n"
                    f"📦 ပက်ကေ့ချ်: {package['name']}\n"
                    f"📅 ကာလ: {package['days']} ရက်\n"
                    f"💎 သုံးခဲ့သည့် ခရက်ဒစ်: {package['credits']}\n"
                    f"💰 ကျန်ငွေ: {new_credits} credits\n\n"
                    f"✅ *VPN ကိုအသုံးပြုနိုင်ပါပြီ*\n\n"
                    f"*မှတ်ချက်:* VPN app ထဲက token ကို admin ထံပို့ပါ",
                    parse_mode='Markdown'
                )
                
                # Ask for token
                context.bot.send_message(
                    chat_id=user_id,
                    text="🔑 *VPN Token တောင်းခံခြင်း*\n\n"
                         "ကျေးဇူးပြု၍ VPN app ထဲမှ token ကို အောက်ပါအတိုင်းပို့ပါ:\n\n"
                         "`/sendtoken YOUR_VPN_TOKEN`\n\n"
                         "*ဥပမာ:*\n"
                         "`/sendtoken ABC123XYZ789`",
                    parse_mode='Markdown'
                )
                
            else:
                needed = package['credits'] - credits
                query.edit_message_text(
                    f"❌ *ငွေမလုံလောက်ပါ*\n\n"
                    f"📦 ပက်ကေ့ချ်: {package['name']}\n"
                    f"💎 လိုအပ်ငွေ: {package['credits']} credits\n"
                    f"💰 သင့်လက်ကျန်: {credits} credits\n"
                    f"📈 လိုအပ်သောငွေ: {needed} credits\n\n"
                    f"ကျေးဇူးပြု၍ ငွေဖြည့်သွင်းပါ:",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("💰 ငွေဖြည့်ရန်", callback_data='add_money')],
                        [InlineKeyboardButton("🔙 နောက်သို့", callback_data='buy_vip')]
                    ])
                )
    
    elif data == 'send_screenshot':
        user_states[user_id] = 'waiting_screenshot'
        query.edit_message_text(
            "📸 *ငွေလွှဲ Screenshot ပို့ရန်*\n\n"
            "ကျေးဇူးပြု၍ ငွေလွှဲထားသည့် screenshot ကို ပုံအဖြစ်ပို့ပါ။\n\n"
            "*မှတ်ချက်:* Screenshot ထဲတွင် ငွေလွှဲနံပါတ်၊ ငွေပမာဏ ပြည့်စုံစွာပါရပါမည်။",
            parse_mode='Markdown'
        )
    
    query.answer()

# ========================
# MESSAGE HANDLERS
# ========================
def handle_message(update, context):
    """Handle messages and photos"""
    user_id = update.effective_user.id
    message = update.message
    
    # Check if user is waiting for screenshot
    if user_states.get(user_id) == 'waiting_screenshot' and message.photo:
        # Forward to admin
        caption = (
            f"📸 *ငွေလွှဲ Screenshot*\n\n"
            f"👤 အသုံးပြုသူ: {update.effective_user.first_name}\n"
            f"🆔 အိုင်ဒီ: `{user_id}`\n"
            f"📅 အချိန်: {update.message.date}"
        )
        
        # Forward photo to admin
        context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=message.photo[-1].file_id,
            caption=caption,
            parse_mode='Markdown'
        )
        
        # Notify user
        update.message.reply_text(
            "✅ *Screenshot လက်ခံရရှိပါပြီ*\n\n"
            "Admin မှစစ်ဆေးပြီး ခရက်ဒစ်ထည့်ပေးပါမည်။\n"
            "မိနစ်အနည်းငယ်စောင့်ပါ။",
            parse_mode='Markdown'
        )
        
        # Reset state
        user_states[user_id] = None
        
        return
    
    # Check if message contains token command
    if message.text and message.text.startswith('/token'):
        parts = message.text.split()
        if len(parts) >= 4:
            try:
                token = parts[1]
                days = int(parts[2])
                price = int(parts[3])
                
                # Create token request
                req_id = create_request(user_id, token, days, price)
                
                # Notify admin
                admin_msg = (
                    f"🔔 *Token တောင်းခံမှု*\n\n"
                    f"👤 အသုံးပြုသူ: {update.effective_user.first_name}\n"
                    f"🆔 အိုင်ဒီ: `{user_id}`\n"
                    f"📌 တောင်းခံချက် ID: `{req_id}`\n"
                    f"🔑 Token: `{token[:10]}...`\n"
                    f"📅 ရက်: {days}\n"
                    f"💰 စျေးနှုန်း: {price} credits\n\n"
                    f"*အတည်ပြုရန်:* `/approve {req_id}`"
                )
                
                context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=admin_msg,
                    parse_mode='Markdown'
                )
                
                update.message.reply_text(
                    f"✅ *Token တင်သွင်းပြီးပါပြီ*\n\n"
                    f"📌 တောင်းခံချက် ID: `{req_id}`\n"
                    f"⏳ Admin အတည်ပြုချက်စောင့်ဆိုင်းနေပါသည်",
                    parse_mode='Markdown'
                )
                
            except Exception as e:
                update.message.reply_text(f"❌ မှားယွင်းမှု: {str(e)}")
        
        return
    
    # Check if message contains sendtoken command
    if message.text and message.text.startswith('/sendtoken'):
        parts = message.text.split()
        if len(parts) >= 2:
            token = parts[1]
            
            # Forward to admin
            admin_msg = (
                f"🔑 *VPN Token ရရှိပါပြီ*\n\n"
                f"👤 အသုံးပြုသူ: {update.effective_user.first_name}\n"
                f"🆔 အိုင်ဒီ: `{user_id}`\n"
                f"🔑 Token: `{token}`\n\n"
                f"*မှတ်ချက်:* User သည် VIP ဝယ်ယူပြီးဖြစ်သည်။"
            )
            
            context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_msg,
                parse_mode='Markdown'
            )
            
            update.message.reply_text(
                "✅ *Token လက်ခံရရှိပါပြီ*\n\n"
                "Admin ထံသို့ပို့ပြီးဖြစ်သည်။\n"
                "VPN configuration အတွက် စောင့်ပါ။",
                parse_mode='Markdown'
            )
        
        return

# ========================
# ADMIN COMMANDS
# ========================
def admin_approve(update, context):
    """Admin approve payment or token"""
    user_id = update.effective_user.id
    
    if str(user_id) != str(ADMIN_ID):
        update.message.reply_text("❌ Admin များသာလုပ်ဆောင်နိုင်ပါသည်")
        return
    
    if len(context.args) < 2:
        update.message.reply_text("အသုံးပြုနည်း: `/approve USER_ID CREDITS`")
        return
    
    try:
        target_user = int(context.args[0])
        credits = int(context.args[1])
        
        # Add credits
        new_balance = add_credits(target_user, credits)
        
        # Notify user
        context.bot.send_message(
            chat_id=target_user,
            text=f"✅ *ငွေဖြည့်သွင်းပြီးပါပြီ*\n\n"
                 f"💰 ဖြည့်သွင်းငွေ: {credits} credits\n"
                 f"💎 စုစုပေါင်းငွေ: {new_balance} credits\n\n"
                 f"VIP ဝယ်ယူရန် အသင့်ဖြစ်ပါပြီ။",
            parse_mode='Markdown'
        )
        
        update.message.reply_text(
            f"✅ User `{target_user}` အား {credits} credits ထည့်ပေးပြီးပါပြီ။\n"
            f"သူ့လက်ကျန်: {new_balance} credits",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        update.message.reply_text(f"❌ မှားယွင်းမှု: {str(e)}")

# ========================
# MAIN FUNCTION
# ========================
def main():
    """Start bot"""
    try:
        updater = Updater(BOT_TOKEN, use_context=True)
        dp = updater.dispatcher
        
        # Command handlers
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("approve", admin_approve))
        
        # Button handler
        dp.add_handler(CallbackQueryHandler(button_handler))
        
        # Message handler
        dp.add_handler(MessageHandler(Filters.text | Filters.photo, handle_message))
        
        print("✅ Bot setup complete")
        print("🔄 Starting polling...")
        
        updater.start_polling()
        
        print("\n" + "=" * 60)
        print("🎉 AUTO VIP SYSTEM IS RUNNING!")
        print("=" * 60)
        print("✨ Features:")
        print("  • ငွေဖြည့်သွင်းစနစ်")
        print("  • VIP ဝယ်ယူစနစ်")
        print("  • Token တင်သွင်းစနစ်")
        print("  • Admin ထိန်းချုပ်စနစ်")
        print("=" * 60)
        
        updater.idle()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
