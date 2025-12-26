# database.py
import requests
import json
from datetime import datetime, timedelta

# -------- Load Config --------
with open("config.json") as f:
    config = json.load(f)

BASE_URL = config["FIREBASE_URL"].rstrip("/")   # sanitize


# -------- Firebase Helpers --------
def fb_url(path: str):
    return f"{BASE_URL}/{path}.json"


def set_user(user_id, data: dict):
    try:
        requests.patch(fb_url(f"users/{user_id}"), json=data, timeout=10)
    except Exception as e:
        print("⚠ Firebase write error:", e)


def get_user(user_id):
    try:
        r = requests.get(fb_url(f"users/{user_id}"), timeout=10)
        return r.json() or {}
    except Exception as e:
        print("⚠ Firebase read error:", e)
        return {}


# -------- Add / Extend VIP --------
def set_user_vip(user_id, days):
    now = datetime.utcnow()

    user = get_user(user_id)

    # already vip → extend from current expiry
    if user.get("vip") and "expiry" in user:
        old = datetime.fromtimestamp(user["expiry"])
        if old > now:
            now = old

    expiry = (now + timedelta(days=days)).timestamp()

    data = {
        "vip": True,
        "expiry": expiry,
        "updated": datetime.utcnow().timestamp()
    }

    set_user(user_id, data)
    return expiry


# -------- Check VIP Status --------
def is_vip(user_id):
    user = get_user(user_id)

    if not user or not user.get("vip"):
        return False

    if datetime.utcnow().timestamp() > user.get("expiry", 0):
        # auto disable expired vip
        set_user(user_id, {"vip": False})
        return False

    return True
