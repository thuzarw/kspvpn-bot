from telegram.ext import Updater, CommandHandler
from datetime import datetime
from config import config
from database import create_request, cut_credits, add_vip, get, set

ADMIN = config["ADMIN_ID"]


def token(update, ctx):
    user = update.effective_user
    user_id = str(user.id)

    if len(ctx.args) < 3:
        return update.message.reply_text(
            "Usage:\n/token <device_id> <days> <price>"
        )

    device = ctx.args[0]
    days = int(ctx.args[1])
    price = int(ctx.args[2])

    req_id = create_request(user_id, device, days, price)

    update.message.reply_text(
        "📝 Request submitted.\n"
        "⏳ Please wait for admin approval."
    )

    ctx.bot.send_message(
        ADMIN,
        f"🔔 New VIP Request\n"
        f"👤 User: {user_id}\n"
        f"🧩 Token: `{device}`\n"
        f"⏳ Days: {days}\n"
        f"💎 Price: {price}\n\n"
        f"/approve {req_id}\n/reject {req_id}",
        parse_mode="Markdown"
    )


def approve(update, ctx):
    if update.effective_user.id != ADMIN:
        return

    req_id = ctx.args[0]
    req = get(f"pending_tokens/{req_id}")

    if not req or req.get("status") != "pending":
        return update.message.reply_text("❌ Invalid request")

    user_id = req["user_id"]

    if not cut_credits(user_id, req["price"]):
        return update.message.reply_text("❌ Not enough credits")

    expiry = add_vip(user_id, req["days"])

    set(f"pending_tokens/{req_id}", {"status": "approved"})

    update.message.reply_text("✔ Approved & VIP Activated")

    update.bot.send_message(
        user_id,
        f"🎉 VIP Activated!\n"
        f"⏳ Expiry: {datetime.utcfromtimestamp(expiry)} UTC"
    )


def reject(update, ctx):
    if update.effective_user.id != ADMIN:
        return

    req_id = ctx.args[0]
    set(f"pending_tokens/{req_id}", {"status": "rejected"})
    update.message.reply_text("❌ Request rejected")


updater = Updater(config["BOT_TOKEN"])
dp = updater.dispatcher

dp.add_handler(CommandHandler("token", token))
dp.add_handler(CommandHandler("approve", approve))
dp.add_handler(CommandHandler("reject", reject))

print("🚀 Bot Running...")
updater.start_polling()
updater.idle()
