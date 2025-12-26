import json
import time
import firebase_admin
from firebase_admin import credentials, firestore
from pyrogram import Client, filters

cfg = json.load(open("config.json"))

cred = credentials.Certificate(cfg["FIREBASE_KEY_FILE"])
firebase_admin.initialize_app(cred)

db = firestore.client()

bot = Client(
    "vpn-bot",
    api_id=12345,
    api_hash="api_hash_dummy",
    bot_token=cfg["BOT_TOKEN"]
)

def get_user(uid):
    ref = db.collection(cfg["FIREBASE_DB"]).document(str(uid))
    user = ref.get()
    if user.exists:
        return ref, user.to_dict()
    return ref, {"credits":0,"vip":False,"expire":0}

def save_user(ref,data):
    ref.set(data)

@bot.on_message(filters.command("start"))
async def start(_, m):
    ref, u = get_user(m.from_user.id)
    text = (
        f"👋 Hello {m.from_user.first_name}\n\n"
        f"💎 Credits: {u['credits']}\n"
        f"🔐 VIP: {'Active' if u['vip'] else 'None'}\n"
    )
    await m.reply(text)

@bot.on_message(filters.command("addcredit") & filters.user(cfg["ADMIN_ID"]))
async def addcredit(_, m):
    try:
        uid, amt = m.text.split()[1:]
        uid=int(uid); amt=int(amt)
        ref,u=get_user(uid)
        u["credits"]+=amt
        save_user(ref,u)
        await m.reply(f"Added {amt} credits to {uid}")
    except:
        await m.reply("Usage: /addcredit user_id amount")

@bot.on_message(filters.command("vip") & filters.user(cfg["ADMIN_ID"]))
async def setvip(_, m):
    try:
        uid, days = m.text.split()[1:]
        uid=int(uid); days=int(days)
        ref,u=get_user(uid)
        u["vip"]=True
        u["expire"]=int(time.time())+(days*86400)
        save_user(ref,u)
        await m.reply(f"VIP enabled {days} days for {uid}")
    except:
        await m.reply("Usage: /vip user_id days")

bot.run()
