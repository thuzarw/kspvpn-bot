import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)
from config import config
from database import create_request, approve_request

logging.basicConfig(level=logging.INFO)

ADMIN = int(config["ADMIN_ID"])
BOT_TOKEN = config["BOT_TOKEN"]


# /start
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"🎉 Welcome {user}!\n"
        f"📌 Commands:\n"
        f"/token <token> <days> <price>\n"
        f"/approve <req_id> (Admin only)"
    )


# /token
async def token_request(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if len(ctx.args) < 3:
        return await update.message.reply_text(
            "Usage:\n/token <token> <days> <price>"
        )

    token = ctx.args[0]
    days = int(ctx.args[1])
    price = int(ctx.args[2])

    rid = create_request(uid, token, days, price)

    await update.message.reply_text(
        f"📝 Token submitted\n"
        f"📌 Request ID: `{rid}`",
        parse_mode="Markdown"
    )


# /approve
async def approve(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN:
        return await update.message.reply_text("❌ Admin only")

    if len(ctx.args) < 1:
        return await update.message.reply_text("Usage:\n/approve <req_id>")

    rid = ctx.args[0]
    result = approve_request(rid)

    await update.message.reply_text(f"Result: {result}")


# Run bot
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("token", token_request))
app.add_handler(CommandHandler("approve", approve))

print("✅ Bot running…")
app.run_polling()
