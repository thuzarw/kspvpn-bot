from telegram.ext import Updater, CommandHandler
from config import config
from database import set_user_vip

ADMIN = config["ADMIN_ID"]

def addvip(update, ctx):
    if update.effective_user.id != ADMIN:
        return update.message.reply_text("❌ Admin only")

    if len(ctx.args) < 2:
        return update.message.reply_text("Usage: /addvip user_id days")

    user_id = ctx.args[0]
    days = int(ctx.args[1])

    expiry = set_user_vip(user_id, days)

    update.message.reply_text(
        f"🎟 VIP added to {user_id}\n⏳ Expiry: {datetime.utcfromtimestamp(expiry)} UTC"
    )

updater = Updater(config["BOT_TOKEN"])
dp = updater.dispatcher
dp.add_handler(CommandHandler("addvip", addvip))
updater.start_polling()
