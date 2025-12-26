import requests
import json
from datetime import datetime, timedelta

with open("config.json") as f:
    config = json.load(f)

BASE_URL = config["firebase_url"]

def set_user_vip(user_id, days):
    expiry = (datetime.utcnow() + timedelta(days=days)).timestamp()

    data = {
        "vip": True,
        "expiry": expiry
    }

    requests.patch(f"{BASE_URL}/users/{user_id}.json", json=data)

def get_user(user_id):
    r = requests.get(f"{BASE_URL}/users/{user_id}.json")
    return r.json() or {}
