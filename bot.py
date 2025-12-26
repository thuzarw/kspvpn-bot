from database import create_request, approve_request
from database import add_vip

# Create token request (user command)
def token_request(update, ctx):
    uid = update.effective_user.id

    if len(ctx.args) < 3:
        return update.message.reply_text("Usage:\n/token <token> <days> <price>")

    token = ctx.args[0]
    days  = int(ctx.args[1])
    price = int(ctx.args[2])

    rid = create_request(uid, token, days, price)

    update.message.reply_text(
        f"📝 Token submitted for review\n"
        f"Request ID: `{rid}`\n"
        f"⏳ Waiting for admin approval",
        parse_mode="Markdown"
    )


# Admin approve
def approve(update, ctx):
    uid = update.effective_user.id
    if uid != ADMIN:
        return update.message.reply_text("❌ Admin only")

    rid = ctx.args[0]
    result = approve_request(rid)

    msgs = {
        "approved": "✅ Request Approved + VIP Added",
        "no_credit": "❌ Not enough credits",
        "already_processed": "⚠ Already processed",
        "not_found": "❌ Invalid request ID"
    }

    update.message.reply_text(msgs.get(result, "Unknown status"))
