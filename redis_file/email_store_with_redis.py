# redis_file/email_store_with_redis.py
from redis_file.redis_client import redis_client
import json
from datetime import datetime, timedelta

def store_email_verification(email: str, otp: int):
    key = f"email_temp:{email}"
    data = {
        "email": email,
        "otp": otp,
        "sent_at": datetime.utcnow().isoformat()
    }

    # Store data as JSON string with 10 min expiry (300 sec)
    redis_client.setex(key, timedelta(minutes=10), json.dumps(data))

def get_email_verification(email: str):
    key = f"email_temp:{email}"
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def delete_email_verification(email: str):
    key = f"email_temp:{email}"
    redis_client.delete(key)