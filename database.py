# =========================
# PAYMENT REQUEST SYSTEM
# =========================
def add_payment_request(user_id, amount, payment_method, proof_text=None):
    """Add payment request"""
    pid = str(int(time.time() * 1000))
    
    payment_data = {
        "user_id": str(user_id),
        "amount": int(amount),
        "payment_method": payment_method,
        "proof": proof_text or "",
        "status": "pending",
        "created": int(time.time()),
        "payment_id": pid
    }
    
    set(f"payment_requests/{pid}", payment_data)
    
    # Also add to user's payment history
    user_payments = get(f"user_payments/{user_id}") or {}
    user_payments[pid] = payment_data
    set(f"user_payments/{user_id}", user_payments)
    
    return pid


def get_payment_request(pid):
    """Get payment request by ID"""
    return get(f"payment_requests/{pid}")


def get_pending_payments():
    """Get all pending payment requests"""
    all_payments = get("payment_requests") or {}
    pending = {}
    
    for pid, payment in all_payments.items():
        if payment.get("status") == "pending":
            pending[pid] = payment
    
    return pending


def get_user_payments(user_id):
    """Get all payment requests by user"""
    return get(f"user_payments/{user_id}") or {}


def approve_payment(pid, admin_id):
    """Approve payment request"""
    payment = get_payment_request(pid)
    
    if not payment:
        return {"success": False, "message": "not_found"}
    
    if payment.get("status") != "pending":
        return {"success": False, "message": "already_processed"}
    
    user_id = payment.get("user_id")
    amount = payment.get("amount", 0)
    
    if not user_id or amount <= 0:
        set(f"payment_requests/{pid}", {"status": "invalid"})
        return {"success": False, "message": "invalid"}
    
    # Add credits to user
    new_balance = add_credits(user_id, amount)
    
    # Update payment status
    approved_data = {
        "status": "approved",
        "approved_at": int(time.time()),
        "approved_by": str(admin_id),
        "user_new_balance": new_balance
    }
    
    set(f"payment_requests/{pid}", approved_data)
    
    # Update in user's payment history
    user_payments = get(f"user_payments/{user_id}") or {}
    if pid in user_payments:
        user_payments[pid].update(approved_data)
        set(f"user_payments/{user_id}", user_payments)
    
    # Log admin action
    log_id = str(int(time.time() * 1000))
    set(f"admin_logs/{log_id}", {
        "action": "approve_payment",
        "admin_id": str(admin_id),
        "user_id": str(user_id),
        "payment_id": pid,
        "amount": amount,
        "new_balance": new_balance,
        "timestamp": int(time.time())
    })
    
    return {"success": True, "message": "approved", "new_balance": new_balance}


def reject_payment(pid, admin_id, reason="rejected"):
    """Reject payment request"""
    payment = get_payment_request(pid)
    
    if not payment:
        return {"success": False, "message": "not_found"}
    
    set(f"payment_requests/{pid}", {
        "status": reason,
        "rejected_at": int(time.time()),
        "rejected_by": str(admin_id),
        "reason": reason
    })
    
    # Update in user's payment history
    user_id = payment.get("user_id")
    if user_id:
        user_payments = get(f"user_payments/{user_id}") or {}
        if pid in user_payments:
            user_payments[pid].update({
                "status": reason,
                "rejected_at": int(time.time()),
                "rejected_by": str(admin_id)
            })
            set(f"user_payments/{user_id}", user_payments)
    
    return {"success": True, "message": "rejected"}


# =========================
# TOKEN SEND SYSTEM (VIP ဝယ်ပြီး token ပို့တာ)
# =========================
def add_vpn_token(user_id, vpn_token):
    """Add VPN token sent by user after VIP purchase"""
    token_id = str(int(time.time() * 1000))
    
    token_data = {
        "user_id": str(user_id),
        "vpn_token": vpn_token,
        "status": "pending",
        "created": int(time.time()),
        "token_id": token_id
    }
    
    set(f"vpn_tokens/{token_id}", token_data)
    
    # Also add to user's token history
    user_tokens = get(f"user_tokens/{user_id}") or {}
    user_tokens[token_id] = token_data
    set(f"user_tokens/{user_id}", user_tokens)
    
    return token_id


def get_vpn_token(token_id):
    """Get VPN token by ID"""
    return get(f"vpn_tokens/{token_id}")


def get_pending_tokens():
    """Get all pending VPN tokens"""
    all_tokens = get("vpn_tokens") or {}
    pending = {}
    
    for token_id, token_data in all_tokens.items():
        if token_data.get("status") == "pending":
            pending[token_id] = token_data
    
    return pending


def get_user_tokens(user_id):
    """Get all VPN tokens by user"""
    return get(f"user_tokens/{user_id}") or {}


def mark_token_processed(token_id, admin_id):
    """Mark VPN token as processed"""
    token = get_vpn_token(token_id)
    
    if not token:
        return False
    
    set(f"vpn_tokens/{token_id}", {
        "status": "processed",
        "processed_at": int(time.time()),
        "processed_by": str(admin_id)
    })
    
    # Update in user's token history
    user_id = token.get("user_id")
    if user_id:
        user_tokens = get(f"user_tokens/{user_id}") or {}
        if token_id in user_tokens:
            user_tokens[token_id].update({
                "status": "processed",
                "processed_at": int(time.time()),
                "processed_by": str(admin_id)
            })
            set(f"user_tokens/{user_id}", user_tokens)
    
    return True


# =========================
# ADMIN DASHBOARD FUNCTIONS
# =========================
def get_admin_dashboard():
    """Get data for admin dashboard"""
    users = get("users") or {}
    payments = get("payment_requests") or {}
    tokens = get("vpn_tokens") or {}
    token_requests = get("pending_tokens") or {}
    
    # Calculate statistics
    stats = {
        "total_users": len(users),
        "vip_users": sum(1 for u in users.values() if u.get("vip")),
        "total_credits": sum(int(u.get("credits", 0)) for u in users.values()),
        
        "pending_payments": sum(1 for p in payments.values() if p.get("status") == "pending"),
        "total_payments": len(payments),
        "payment_amount": sum(int(p.get("amount", 0)) for p in payments.values() if p.get("status") == "approved"),
        
        "pending_tokens": sum(1 for t in tokens.values() if t.get("status") == "pending"),
        "pending_requests": sum(1 for tr in token_requests.values() if tr.get("status") == "pending"),
        
        "recent_users": [],
        "recent_payments": [],
        "recent_tokens": []
    }
    
    # Get recent users (last 10)
    user_list = []
    for uid, user_data in users.items():
        user_list.append({
            "user_id": uid,
            "name": user_data.get("name", "Unknown"),
            "credits": user_data.get("credits", 0),
            "vip": user_data.get("vip", False),
            "created": user_data.get("created_at", 0)
        })
    
    # Sort by creation time
    user_list.sort(key=lambda x: x.get("created", 0), reverse=True)
    stats["recent_users"] = user_list[:10]
    
    # Get recent payments (last 10)
    payment_list = []
    for pid, payment_data in payments.items():
        payment_list.append({
            "payment_id": pid,
            "user_id": payment_data.get("user_id"),
            "amount": payment_data.get("amount", 0),
            "status": payment_data.get("status", "pending"),
            "created": payment_data.get("created", 0)
        })
    
    payment_list.sort(key=lambda x: x.get("created", 0), reverse=True)
    stats["recent_payments"] = payment_list[:10]
    
    # Get recent tokens (last 10)
    token_list = []
    for tid, token_data in tokens.items():
        token_list.append({
            "token_id": tid,
            "user_id": token_data.get("user_id"),
            "status": token_data.get("status", "pending"),
            "created": token_data.get("created", 0)
        })
    
    token_list.sort(key=lambda x: x.get("created", 0), reverse=True)
    stats["recent_tokens"] = token_list[:10]
    
    return stats


# =========================
# USER ACTIVITY LOGGING
# =========================
def log_user_activity(user_id, activity_type, details=None):
    """Log user activity"""
    log_id = str(int(time.time() * 1000))
    
    log_data = {
        "user_id": str(user_id),
        "activity": activity_type,
        "details": details or {},
        "timestamp": int(time.time())
    }
    
    set(f"user_activity/{user_id}/{log_id}", log_data)
    
    # Also update user's last active time
    update_user(user_id, {"last_active": int(time.time())})
    
    return log_id


def get_user_activity(user_id, limit=50):
    """Get user activity logs"""
    activities = get(f"user_activity/{user_id}") or {}
    
    # Convert to list and sort
    activity_list = []
    for log_id, log_data in activities.items():
        activity_list.append({
            "log_id": log_id,
            **log_data
        })
    
    # Sort by timestamp
    activity_list.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    
    return activity_list[:limit]


# =========================
# NOTIFICATION SYSTEM
# =========================
def add_notification(user_id, notification_type, message, data=None):
    """Add notification for user"""
    notif_id = str(int(time.time() * 1000))
    
    notif_data = {
        "user_id": str(user_id),
        "type": notification_type,
        "message": message,
        "data": data or {},
        "status": "unread",
        "created": int(time.time()),
        "notification_id": notif_id
    }
    
    set(f"notifications/{user_id}/{notif_id}", notif_data)
    
    return notif_id


def get_user_notifications(user_id, unread_only=False):
    """Get user notifications"""
    notifications = get(f"notifications/{user_id}") or {}
    
    notif_list = []
    for notif_id, notif_data in notifications.items():
        if unread_only and notif_data.get("status") != "unread":
            continue
        
        notif_list.append({
            "notification_id": notif_id,
            **notif_data
        })
    
    # Sort by creation time
    notif_list.sort(key=lambda x: x.get("created", 0), reverse=True)
    
    return notif_list


def mark_notification_read(user_id, notification_id):
    """Mark notification as read"""
    notification = get(f"notifications/{user_id}/{notification_id}")
    
    if notification:
        set(f"notifications/{user_id}/{notification_id}", {
            **notification,
            "status": "read",
            "read_at": int(time.time())
        })
        return True
    
    return False


# =========================
# BULK OPERATIONS
# =========================
def bulk_add_credits(user_credits_dict, admin_id, reason="bulk_add"):
    """Add credits to multiple users at once"""
    results = {}
    logs = []
    
    for user_id, amount in user_credits_dict.items():
        try:
            new_balance = add_credits(user_id, amount)
            results[str(user_id)] = {
                "success": True,
                "new_balance": new_balance,
                "amount": amount
            }
            
            # Add notification
            add_notification(
                user_id,
                "credits_added",
                f"Admin မှ သင့်အကောင့်သို့ credits {amount} ထည့်ပေးပြီးပါပြီ။",
                {"amount": amount, "new_balance": new_balance}
            )
            
            # Log admin action
            log_id = str(int(time.time() * 1000))
            logs.append({
                "log_id": log_id,
                "action": "bulk_add_credits",
                "admin_id": str(admin_id),
                "user_id": str(user_id),
                "amount": amount,
                "new_balance": new_balance,
                "reason": reason,
                "timestamp": int(time.time())
            })
            
        except Exception as e:
            results[str(user_id)] = {
                "success": False,
                "error": str(e),
                "amount": amount
            }
    
    # Save all logs
    for log_data in logs:
        set(f"admin_logs/{log_data['log_id']}", log_data)
    
    return results


def bulk_set_vip(user_days_dict, admin_id, reason="bulk_set"):
    """Set VIP for multiple users at once"""
    results = {}
    logs = []
    
    for user_id, days in user_days_dict.items():
        try:
            expiry = add_vip(user_id, days)
            results[str(user_id)] = {
                "success": True,
                "expiry": expiry,
                "days": days
            }
            
            # Add notification
            add_notification(
                user_id,
                "vip_activated",
                f"Admin မှ သင့်အား VIP {days} ရက် ဖွင့်ပေးပြီးပါပြီ။",
                {"days": days, "expiry": expiry}
            )
            
            # Log admin action
            log_id = str(int(time.time() * 1000))
            logs.append({
                "log_id": log_id,
                "action": "bulk_set_vip",
                "admin_id": str(admin_id),
                "user_id": str(user_id),
                "days": days,
                "expiry": expiry,
                "reason": reason,
                "timestamp": int(time.time())
            })
            
        except Exception as e:
            results[str(user_id)] = {
                "success": False,
                "error": str(e),
                "days": days
            }
    
    # Save all logs
    for log_data in logs:
        set(f"admin_logs/{log_data['log_id']}", log_data)
    
    return results


# =========================
# BACKUP & EXPORT
# =========================
def export_user_data(user_id):
    """Export all user data"""
    user_data = get_user(user_id) or {}
    user_payments = get_user_payments(user_id)
    user_tokens = get_user_tokens(user_id)
    user_requests = get_user_requests(user_id)
    user_activity = get_user_activity(user_id, limit=1000)
    user_notifications = get_user_notifications(user_id)
    
    return {
        "user_info": user_data,
        "payments": user_payments,
        "vpn_tokens": user_tokens,
        "token_requests": user_requests,
        "activity_logs": user_activity,
        "notifications": user_notifications,
        "exported_at": int(time.time())
    }


def export_all_data():
    """Export all system data (admin only)"""
    users = get("users") or {}
    payments = get("payment_requests") or {}
    tokens = get("vpn_tokens") or {}
    token_requests = get("pending_tokens") or {}
    admin_logs = get("admin_logs") or {}
    
    return {
        "users": users,
        "payments": payments,
        "vpn_tokens": tokens,
        "token_requests": token_requests,
        "admin_logs": admin_logs,
        "exported_at": int(time.time()),
        "total_records": {
            "users": len(users),
            "payments": len(payments),
            "vpn_tokens": len(tokens),
            "token_requests": len(token_requests),
            "admin_logs": len(admin_logs)
        }
    }


# =========================
# VALIDATION FUNCTIONS
# =========================
def validate_user_id(user_id):
    """Validate if user ID exists"""
    user = get_user(user_id)
    return user is not None and user != {}


def validate_payment_id(payment_id):
    """Validate if payment ID exists"""
    payment = get_payment_request(payment_id)
    return payment is not None and payment != {}


def validate_token_id(token_id):
    """Validate if token ID exists"""
    token = get_vpn_token(token_id)
    return token is not None and token != {}


def validate_request_id(request_id):
    """Validate if request ID exists"""
    request = get_request(request_id)
    return request is not None and request != {}


# =========================
# UTILITY FUNCTIONS
# =========================
def get_user_by_username(username):
    """Get user by username"""
    users = get("users") or {}
    
    for user_id, user_data in users.items():
        if user_data.get("username") == username:
            return {user_id: user_data}
    
    return {}


def search_users(search_term):
    """Search users by name or username"""
    users = get("users") or {}
    results = {}
    
    search_term = search_term.lower()
    
    for user_id, user_data in users.items():
        name = user_data.get("name", "").lower()
        username = user_data.get("username", "").lower()
        
        if (search_term in name or 
            search_term in username or 
            search_term in str(user_id)):
            results[user_id] = user_data
    
    return results


def get_user_summary(user_id):
    """Get comprehensive user summary"""
    user_data = get_user(user_id) or {}
    vip_info = get_vip_status(user_id)
    stats = get_user_stats(user_id)
    
    return {
        "user_info": user_data,
        "vip_status": vip_info,
        "statistics": stats,
        "credits": user_data.get("credits", 0),
        "is_vip": vip_info.get("vip", False),
        "vip_expiry": vip_info.get("expiry", 0),
        "total_requests": stats.get("total_requests", 0),
        "approved_requests": stats.get("approved_requests", 0)
    }


# =========================
# CLEANUP FUNCTIONS (Extended)
# =========================
def cleanup_old_notifications(days=30):
    """Clean up old notifications"""
    all_users = get("users") or {}
    cutoff = int(time.time()) - (days * 24 * 60 * 60)
    deleted = 0
    
    for user_id in all_users.keys():
        notifications = get(f"notifications/{user_id}") or {}
        for notif_id, notif_data in list(notifications.items()):
            created = notif_data.get("created", 0)
            if created < cutoff:
                delete(f"notifications/{user_id}/{notif_id}")
                deleted += 1
    
    return deleted


def cleanup_old_activity_logs(days=90):
    """Clean up old activity logs"""
    all_users = get("users") or {}
    cutoff = int(time.time()) - (days * 24 * 60 * 60)
    deleted = 0
    
    for user_id in all_users.keys():
        activities = get(f"user_activity/{user_id}") or {}
        for log_id, log_data in list(activities.items()):
            timestamp = log_data.get("timestamp", 0)
            if timestamp < cutoff:
                delete(f"user_activity/{user_id}/{log_id}")
                deleted += 1
    
    return deleted


def cleanup_old_admin_logs(days=180):
    """Clean up old admin logs"""
    admin_logs = get("admin_logs") or {}
    cutoff = int(time.time()) - (days * 24 * 60 * 60)
    deleted = 0
    
    for log_id, log_data in list(admin_logs.items()):
        timestamp = log_data.get("timestamp", 0)
        if timestamp < cutoff:
            delete(f"admin_logs/{log_id}")
            deleted += 1
    
    return deleted


def run_all_cleanup():
    """Run all cleanup functions"""
    results = {
        "expired_vip": cleanup_expired_vip(),
        "old_requests": cleanup_old_requests(),
        "old_notifications": cleanup_old_notifications(),
        "old_activity_logs": cleanup_old_activity_logs(),
        "old_admin_logs": cleanup_old_admin_logs()
    }
    
    return results


# =========================
# TESTING FUNCTIONS
# =========================
def create_test_user(user_id=None, credits=100, vip=False):
    """Create a test user for development"""
    if user_id is None:
        user_id = int(time.time())
    
    test_user = {
        "name": f"TestUser{user_id}",
        "credits": credits,
        "vip": vip,
        "expiry": int(time.time()) + (30 * 24 * 60 * 60) if vip else 0,
        "created_at": int(time.time()),
        "last_active": int(time.time())
    }
    
    set(f"users/{user_id}", test_user)
    return user_id, test_user


def create_test_payment(user_id=None, amount=50):
    """Create a test payment request"""
    if user_id is None:
        user_id = int(time.time())
    
    return add_payment_request(user_id, amount, "test_kbz", "Test payment proof")


def create_test_token(user_id=None, token="TEST123456"):
    """Create a test VPN token"""
    if user_id is None:
        user_id = int(time.time())
    
    return add_vpn_token(user_id, token)


def create_test_request(user_id=None):
    """Create a test token request"""
    if user_id is None:
        user_id = int(time.time())
    
    return create_request(user_id, "TESTTOKEN123", 30, 100)
