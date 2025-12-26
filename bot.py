from telegram.ext import Updater, CommandHandler
from config import config
from database import create_request, approve_request, add_vip

ADMIN = int(config["ADMIN_ID"])


# =========================
# START MENU
# =========================
def start(update, ctx):
    uid = update.effective_user.id
    name = update.effective_user.first_name

    update.message.reply_text(
        f"🎉 Welcome {name}!\n"
        f"🤖 KSP VPN Bot သို့ကြိုဆိုပါတယ်\n\n"
        f"📌 Available Commands:\n"
        f"/token <token> <days> <price>\n"
        f"/approve <req_id>  (Admin Only)"
    )


# =========================
# USER — Submit Token Request
# =========================
def token_request(update, ctx):
    uid = update.effective_user.id

    if len(ctx.args) < 3:
        return update.message.reply_text("Usage:\n/token <token> <days> <price>")

    token = ctx.args[0]
    days  = int(ctx.args[1])
    price = int(ctx.args[2])

    rid = create_request(uid, token, days, price)

    update.message.reply_text(
        f"📝 Token submitted\n"
        f"📌 Request ID: `{rid}`\n"
        f"⏳ Waiting for admin approval",
        parse_mode="Markdown"
    )


# =========================
# ADMIN — Approve Request
# =========================
def approve(update, ctx):
    if update.effective_user.id != ADMIN:
        return update.message.reply_text("❌ Admin only")

    rid = ctx.args[0]
    result = approve_request(rid)

    update.message.reply_text(f"Result: {result}")


# =========================
# BOT RUN
# =========================
updater = Updater(config["BOT_TOKEN"])
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("token", token_request))
dp.add_handler(CommandHandler("approve", approve))

print("✅ Bot started...")
updater.start_polling()
updater.idle()
