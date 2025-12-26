# database.py
import requests
import json
from datetime import datetime, timedelta

# Load config.json
with open("config.json") as f:
    config = json.load(f)

BASE_URL = config["FIREBASE_URL"]   # e.g. https://vpnid-3004d-default-rtdb.firebaseio.com


# Save / Update User record
def set_user(user_id, data: dict):
    requests.patch(f"{BASE_URL}/users/{user_id}.json", json=data)


# Read User
def get_user(user_id):
    r = requests.get(f"{BASE_URL}/users/{user_id}.json")
    return r.json() or {}


# Add VIP Days
def set_user_vip(user_id, days):
    now = datetime.utcnow()

    user = get_user(user_id)

    # If already VIP → extend from old expiry
    if "expiry" in user and user.get("vip") is True:
        start_time = datetime.fromtimestamp(user["expiry"])
        if start_time > now:
            now = start_time

    expiry = (now + timedelta(days=days)).timestamp()

    data = {
        "vip": True,
        "expiry": expiry
    }

    set_user(user_id, data)
    return expiry


# Check VIP Status
def is_vip(user_id):
    user = get_user(user_id)

    if not user or "vip" not in user:
        return False

    if user["vip"] is not True:
        return False

    if datetime.utcnow().timestamp() > user["expiry"]:
        # Auto remove expired VIP
        set_user(user_id, {"vip": False})
        return False

    return True
