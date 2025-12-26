from telegram.ext import Updater, CommandHandler
import json

print("Testing bot setup...")

with open("config.json") as f:
    config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]

def start(update, context):
    update.message.reply_text("Test successful!")

try:
    # Try different syntaxes
    print("Method 1: bot_token parameter")
    updater = Updater(bot_token=BOT_TOKEN, use_context=True)
    
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    
    print("✅ Updater created successfully!")
    print(f"Bot token: {BOT_TOKEN[:10]}...")
    
    # Quick test
    print("\nQuick API test...")
    import requests
    response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe")
    print(f"API Response: {response.status_code}")
    print(f"Bot info: {response.json()}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"\nTrying method 2...")
    
    try:
        # Alternative method
        from telegram import Bot
        bot = Bot(token=BOT_TOKEN)
        print(f"✅ Bot object created: {bot.get_me()}")
    except Exception as e2:
        print(f"❌ Also failed: {e2}")
