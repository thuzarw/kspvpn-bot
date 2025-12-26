import requests, json, time
from datetime import datetime, timedelta

with open("config.json") as f:
    config = json.load(f)

BASE = config["FIREBASE_DB"].rstrip("/")


def db(path):
    return f"{BASE}/{path}.json"


def get(path):
    r = requests.get(db(path))
    return r.json() or {}


def set(path, data):
    requests.patch(db(path), json=data)


# =========================
# CREDIT SYSTEM
# =========================
def cut_credits(user_id, amount):
    user = get(f"users/{user_id}")
    bal = int(user.get("credits", 0))

    if bal < amount:
        return False

    set(f"users/{user_id}", {"credits": bal - amount})
    return True


# =========================
# VIP SYSTEM
# =========================
def add_vip(user_id, days):
    now = datetime.utcnow()
    user = get(f"users/{user_id}")

    if user.get("vip") and user.get("expiry"):
        exp = datetime.fromtimestamp(user["expiry"])
        if exp > now:
            now = exp

    expiry = (now + timedelta(days=days)).timestamp()

    set(f"users/{user_id}", {
        "vip": True,
        "expiry": expiry
    })

    return expiry


# =========================
# TOKEN REQUEST SYSTEM
# =========================
def create_request(user_id, token, days, price):
    rid = str(int(time.time() * 1000))

    set(f"pending_tokens/{rid}", {
        "user_id": user_id,
        "token": token,
        "days": days,
        "price": price,
        "status": "pending",
        "created": int(time.time())
    })

    return rid


def approve_request(rid):
    req = get(f"pending_tokens/{rid}")

    if not req:
        return "not_found"

    if req.get("status") != "pending":
        return "already_processed"

    user_id = req["user_id"]
    price = int(req["price"])
    days = int(req["days"])

    # deduct credits
    if not cut_credits(user_id, price):
        set(f"pending_tokens/{rid}", {"status": "rejected_no_credit"})
        return "no_credit"

    # add vip
    expiry = add_vip(user_id, days)

    # update status
    set(f"pending_tokens/{rid}", {
        "status": "approved",
        "approved_at": int(time.time()),
        "expiry": expiry
    })

    return "approved"
