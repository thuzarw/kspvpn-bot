import requests, json, time
from datetime import datetime, timedelta

with open("config.json") as f:
    config = json.load(f)

BASE = config["FIREBASE_DB"]


def db(path):
    return f"{BASE}/{path}.json"


def get(path):
    return requests.get(db(path)).json() or {}


def set(path, data):
    requests.patch(db(path), json=data)


def cut_credits(user_id, amount):
    user = get(f"users/{user_id}")
    bal = int(user.get("credits", 0))

    if bal < amount:
        return False

    set(f"users/{user_id}", {"credits": bal - amount})
    return True


def add_vip(user_id, days):
    now = datetime.utcnow()
    user = get(f"users/{user_id}")

    if user.get("vip") and "expiry" in user:
        exp = datetime.fromtimestamp(user["expiry"])
        if exp > now:
            now = exp

    expiry = (now + timedelta(days=days)).timestamp()

    set(f"users/{user_id}", {
        "vip": True,
        "expiry": expiry
    })

    return expiry


def create_request(user_id, token, days, price):
    rid = str(int(time.time()*1000))

    set(f"pending_tokens/{rid}", {
        "user_id": user_id,
        "token": token,
        "days": days,
        "price": price,
        "status": "pending"
    })

    return rid
