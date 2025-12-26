from telegram.ext import Updater, CommandHandler
from config import config
from database import set_user_vip
from datetime import datetime   # ← REQUIRED

ADMIN = config["ADMIN_ID"]      # your admin id

def addvip(update, context):
    user = update.effective_user.id

    if user != ADMIN:
        return update.message.reply_text("❌ Admin only")

    if len(context.args) < 2:
        return update.message.reply_text("Usage: /addvip user_id days")

    user_id = context.args[0]
    days = int(context.args[1])

    expiry = set_user_vip(user_id, days)

    update.message.reply_text(
        f"🎟 VIP added to {user_id}\n"
        f"⏳ Expiry: {datetime.utcfromtimestamp(expiry)} UTC"
    )

updater = Updater(config["BOT_TOKEN"], use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("addvip", addvip))

print("🤖 Bot is running…")
updater.start_polling()
updater.idle()
