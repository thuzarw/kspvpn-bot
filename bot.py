from telegram.ext import Updater, CommandHandler
from datetime import datetime
from config import config

from database import (
    set_user_vip,
    add_vip,
    create_request,
    approve_request
)

ADMIN = int(config["ADMIN_ID"])


# =========================
# START
# =========================
def start(update, ctx):
    uid = update.effective_user.id
    name = update.effective_user.first_name

    update.message.reply_text(
        f"🎉 Welcome {name}!\n\n"
        "📌 Available Commands:\n"
        "/token <token> <days> <price>\n"
        "/approve <request_id>  (Admin)\n"
        "/addvip <user_id> <days>"
    )


# =========================
# MANUAL VIP ADD (ADMIN)
# =========================
def addvip(update, ctx):
    uid = update.effective_user.id
    if uid != ADMIN:
        return update.message.reply_text("❌ Admin only")

    if len(ctx.args) < 2:
        return update.message.reply_text("Usage:\n/addvip <user_id> <days>")

    user_id = ctx.args[0]
    days = int(ctx.args[1])

    expiry = set_user_vip(user_id, days)

    update.message.reply_text(
        f"🎟 VIP added to {user_id}\n"
        f"⏳ Expiry: {datetime.utcfromtimestamp(expiry)} UTC"
    )


# =========================
# USER — Submit Token Request
# =========================
def token_request(update, ctx):
    uid = update.effective_user.id

    if len(ctx.args) < 3:
        return update.message.reply_text("Usage:\n/token <token> <days> <price>")

    try:
        token = ctx.args[0]
        days  = int(ctx.args[1])
        price = int(ctx.args[2])
    except:
        return update.message.reply_text("❌ Invalid inputs")

    if days <= 0 or price <= 0:
        return update.message.reply_text("❌ Days & price must be greater than 0")

    rid = create_request(uid, token, days, price)

    update.message.reply_text(
        f"📝 Token submitted for review\n"
        f"🆔 Request ID: `{rid}`\n"
        f"⏳ Waiting for admin approval…",
        parse_mode="Markdown"
    )


# =========================
# ADMIN — Approve Request
# =========================
def approve(update, ctx):
    uid = update.effective_user.id

    if uid != ADMIN:
        return update.message.reply_text("❌ Admin only")

    if len(ctx.args) < 1:
        return update.message.reply_text("Usage:\n/approve <request_id>")

    rid = ctx.args[0]
    result = approve_request(rid)

    messages = {
        "approved": "✅ Request approved — VIP added successfully",
        "no_credit": "❌ User does not have enough credits",
        "invalid": "❌ Request data invalid",
        "already_processed": "⚠ Request already processed",
        "not_found": "❌ Request ID not found"
    }

    update.message.reply_text(messages.get(result, "⚠ Unknown status"))


# =========================
# RUN BOT
# =========================
updater = Updater(config["BOT_TOKEN"])
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("addvip", addvip))
dp.add_handler(CommandHandler("token", token_request))
dp.add_handler(CommandHandler("approve", approve))

print("🤖 Bot started…")
updater.start_polling()
updater.idle()
