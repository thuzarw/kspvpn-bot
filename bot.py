import logging
from telegram.ext import Updater, CommandHandler
from config import config
from database import create_request, approve_request

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

ADMIN = int(config["ADMIN_ID"])
BOT_TOKEN = config["BOT_TOKEN"]


# =========================
# /start
# =========================
def start(update, ctx):
    user = update.effective_user.first_name
    update.message.reply_text(
        f"🎉 Welcome {user}!\n"
        f"🤖 KSP VIP VPN Bot\n\n"
        f"📌 Commands\n"
        f"/token <token> <days> <price>\n"
        f"/approve <req_id>  (Admin only)"
    )


# =========================
# /token
# =========================
def token_request(update, ctx):
    uid = update.effective_user.id

    if len(ctx.args) < 3:
        return update.message.reply_text(
            "Usage:\n/token <token> <days> <price>"
        )

    try:
        token = ctx.args[0]
        days = int(ctx.args[1])
        price = int(ctx.args[2])
    except:
        return update.message.reply_text("❌ Invalid values")

    rid = create_request(uid, token, days, price)

    update.message.reply_text(
        f"📝 Token submitted\n"
        f"📌 Request ID: `{rid}`\n"
        f"⏳ Waiting for admin approval",
        parse_mode="Markdown"
    )


# =========================
# /approve
# =========================
def approve(update, ctx):
    if update.effective_user.id != ADMIN:
        return update.message.reply_text("❌ Admin only")

    if len(ctx.args) < 1:
        return update.message.reply_text("Usage:\n/approve <req_id>")

    rid = ctx.args[0]
    result = approve_request(rid)

    update.message.reply_text(f"Result: {result}")


# =========================
# BOT RUN
# =========================
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("token", token_request))
    dp.add_handler(CommandHandler("approve", approve))

    print("✅ Bot started…")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
