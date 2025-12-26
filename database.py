import requests, json, time
from datetime import datetime, timedelta

with open("config.json") as f:
    config = json.load(f)

BASE = config["FIREBASE_DB"].rstrip("/")


def db(path):
    return f"{BASE}/{path}.json"


def get(path):
    try:
        r = requests.get(db(path), timeout=10)
        return r.json() or {}
    except Exception:
        return {}


def set(path, data):
    try:
        requests.patch(db(path), json=data, timeout=10)
    except Exception:
        pass


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

    exp_raw = user.get("expiry")

    # existing vip → extend from current expiry
    if user.get("vip") and exp_raw:

        try:
            exp = datetime.fromtimestamp(float(exp_raw))
        except Exception:
            exp = now

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
        "user_id": str(user_id),
        "token": str(token),
        "days": int(days),
        "price": int(price),
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

    user_id = req.get("user_id")
    price = int(req.get("price", 0))
    days = int(req.get("days", 0))

    if not user_id or days <= 0:
        set(f"pending_tokens/{rid}", {"status": "invalid_data"})
        return "invalid"

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
