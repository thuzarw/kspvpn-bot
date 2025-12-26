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


def delete(path):
    try:
        requests.delete(db(path), timeout=10)
    except Exception:
        pass


# =========================
# USER MANAGEMENT
# =========================
def get_user(user_id):
    """Get user data"""
    return get(f"users/{user_id}")


def update_user(user_id, data):
    """Update user data"""
    set(f"users/{user_id}", data)


def create_user(user_id, user_data=None):
    """Create new user if not exists"""
    user = get_user(user_id)
    if not user:
        default_data = {
            "credits": 0,
            "vip": False,
            "expiry": 0,
            "created_at": int(time.time()),
            "last_active": int(time.time())
        }
        if user_data:
            default_data.update(user_data)
        set(f"users/{user_id}", default_data)
        return default_data
    return user


# =========================
# CREDIT SYSTEM
# =========================
def get_credits(user_id):
    """Get user credits"""
    user = get_user(user_id) or {}
    return int(user.get("credits", 0))


def add_credits(user_id, amount):
    """Add credits to user account"""
    user = get_user(user_id) or {}
    current = int(user.get("credits", 0))
    new_balance = current + amount
    
    update_user(user_id, {"credits": new_balance})
    return new_balance


def cut_credits(user_id, amount):
    """Deduct credits from user account"""
    user = get_user(user_id) or {}
    bal = int(user.get("credits", 0))

    if bal < amount:
        return False

    update_user(user_id, {"credits": bal - amount})
    return True


def transfer_credits(from_user, to_user, amount):
    """Transfer credits between users"""
    # Check sender balance
    if not cut_credits(from_user, amount):
        return False
    
    # Add to receiver
    add_credits(to_user, amount)
    return True


# =========================
# VIP SYSTEM
# =========================
def get_vip_status(user_id):
    """Get VIP status and expiry"""
    user = get_user(user_id) or {}
    is_vip = user.get("vip", False)
    expiry = user.get("expiry", 0)
    
    # Check if VIP is expired
    if is_vip and expiry:
        try:
            expiry_time = datetime.fromtimestamp(float(expiry))
            if expiry_time < datetime.utcnow():
                # VIP expired
                update_user(user_id, {"vip": False})
                return {"vip": False, "expiry": 0, "expired": True}
        except:
            pass
    
    return {"vip": is_vip, "expiry": expiry, "expired": False}


def add_vip(user_id, days):
    """Add or extend VIP"""
    now = datetime.utcnow()
    user = get_user(user_id) or {}

    exp_raw = user.get("expiry", 0)
    current_vip = user.get("vip", False)

    # If user already has VIP, extend from current expiry
    if current_vip and exp_raw:
        try:
            exp = datetime.fromtimestamp(float(exp_raw))
            if exp > now:
                now = exp  # Extend from current expiry
        except Exception:
            pass

    expiry = (now + timedelta(days=days)).timestamp()
    
    update_user(user_id, {
        "vip": True,
        "expiry": expiry,
        "vip_added": int(time.time()),
        "vip_days": days
    })

    return expiry


def remove_vip(user_id):
    """Remove VIP status"""
    update_user(user_id, {"vip": False, "expiry": 0})


def get_vip_users():
    """Get all VIP users"""
    users = get("users") or {}
    vip_users = {}
    
    for user_id, user_data in users.items():
        if user_data.get("vip"):
            vip_users[user_id] = user_data
    
    return vip_users


# =========================
# TOKEN REQUEST SYSTEM
# =========================
def create_request(user_id, token, days, price):
    """Create token request"""
    rid = str(int(time.time() * 1000))
    
    request_data = {
        "user_id": str(user_id),
        "token": str(token),
        "days": int(days),
        "price": int(price),
        "status": "pending",
        "created": int(time.time()),
        "request_id": rid
    }

    set(f"pending_tokens/{rid}", request_data)
    
    # Also add to user's requests history
    user_requests = get(f"user_requests/{user_id}") or {}
    user_requests[rid] = request_data
    set(f"user_requests/{user_id}", user_requests)
    
    return rid


def get_request(rid):
    """Get token request by ID"""
    return get(f"pending_tokens/{rid}")


def get_pending_requests():
    """Get all pending requests"""
    all_requests = get("pending_tokens") or {}
    pending = {}
    
    for rid, req in all_requests.items():
        if req.get("status") == "pending":
            pending[rid] = req
    
    return pending


def get_user_requests(user_id):
    """Get all requests by user"""
    return get(f"user_requests/{user_id}") or {}


def approve_request(rid):
    """Approve token request"""
    req = get_request(rid)

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
    approved_data = {
        "status": "approved",
        "approved_at": int(time.time()),
        "approved_by": "system",
        "expiry": expiry
    }
    
    set(f"pending_tokens/{rid}", approved_data)
    
    # Update in user's requests
    user_requests = get(f"user_requests/{user_id}") or {}
    if rid in user_requests:
        user_requests[rid].update(approved_data)
        set(f"user_requests/{user_id}", user_requests)

    return "approved"


def reject_request(rid, reason="rejected"):
    """Reject token request"""
    req = get_request(rid)
    if not req:
        return "not_found"
    
    set(f"pending_tokens/{rid}", {
        "status": reason,
        "rejected_at": int(time.time())
    })
    
    # Update in user's requests
    user_id = req.get("user_id")
    if user_id:
        user_requests = get(f"user_requests/{user_id}") or {}
        if rid in user_requests:
            user_requests[rid].update({"status": reason, "rejected_at": int(time.time())})
            set(f"user_requests/{user_id}", user_requests)
    
    return "rejected"


# =========================
# STATISTICS & ANALYTICS
# =========================
def get_stats():
    """Get system statistics"""
    users = get("users") or {}
    requests = get("pending_tokens") or {}
    
    total_users = len(users)
    total_credits = sum(int(user.get("credits", 0)) for user in users.values())
    vip_users = sum(1 for user in users.values() if user.get("vip"))
    
    pending_requests = sum(1 for req in requests.values() if req.get("status") == "pending")
    approved_requests = sum(1 for req in requests.values() if req.get("status") == "approved")
    
    return {
        "total_users": total_users,
        "total_credits": total_credits,
        "vip_users": vip_users,
        "pending_requests": pending_requests,
        "approved_requests": approved_requests
    }


def get_user_stats(user_id):
    """Get user statistics"""
    user = get_user(user_id) or {}
    user_requests = get_user_requests(user_id)
    
    total_requests = len(user_requests)
    approved_requests = sum(1 for req in user_requests.values() if req.get("status") == "approved")
    pending_requests = sum(1 for req in user_requests.values() if req.get("status") == "pending")
    
    return {
        "user_id": user_id,
        "credits": user.get("credits", 0),
        "vip": user.get("vip", False),
        "expiry": user.get("expiry", 0),
        "total_requests": total_requests,
        "approved_requests": approved_requests,
        "pending_requests": pending_requests
    }


# =========================
# ADMIN FUNCTIONS
# =========================
def admin_add_credits(user_id, amount, reason="admin_add"):
    """Admin add credits to user"""
    new_balance = add_credits(user_id, amount)
    
    # Log admin action
    log_id = str(int(time.time() * 1000))
    set(f"admin_logs/{log_id}", {
        "action": "add_credits",
        "admin_id": "system",
        "user_id": str(user_id),
        "amount": amount,
        "new_balance": new_balance,
        "reason": reason,
        "timestamp": int(time.time())
    })
    
    return new_balance


def admin_set_vip(user_id, days, reason="admin_add"):
    """Admin set VIP for user"""
    expiry = add_vip(user_id, days)
    
    # Log admin action
    log_id = str(int(time.time() * 1000))
    set(f"admin_logs/{log_id}", {
        "action": "set_vip",
        "admin_id": "system",
        "user_id": str(user_id),
        "days": days,
        "expiry": expiry,
        "reason": reason,
        "timestamp": int(time.time())
    })
    
    return expiry


# =========================
# CLEANUP FUNCTIONS
# =========================
def cleanup_expired_vip():
    """Clean up expired VIP users"""
    users = get("users") or {}
    updated = 0
    
    for user_id, user_data in users.items():
        if user_data.get("vip") and user_data.get("expiry"):
            try:
                expiry_time = datetime.fromtimestamp(float(user_data["expiry"]))
                if expiry_time < datetime.utcnow():
                    update_user(user_id, {"vip": False})
                    updated += 1
            except:
                pass
    
    return updated


def cleanup_old_requests(days=30):
    """Clean up old requests"""
    requests_data = get("pending_tokens") or {}
    cutoff = int(time.time()) - (days * 24 * 60 * 60)
    deleted = 0
    
    for rid, req in list(requests_data.items()):
        created = req.get("created", 0)
        if created < cutoff:
            delete(f"pending_tokens/{rid}")
            deleted += 1
    
    return deleted
