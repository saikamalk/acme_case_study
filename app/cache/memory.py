import json
from app.cache.redis_client import redis_client


def save_message(username: str, role: str, message: str):
    key = f"session:{username}"
    existing = redis_client.get(key)
    if existing:
        history = json.loads(existing)
    else:
        history = []
    history.append({
        "role": role,
        "message": message
    })
    history = history[-10:]
    redis_client.set(
        key,
        json.dumps(history)
    )


def get_conversation_history(username: str):
    key = f"session:{username}"
    existing = redis_client.get(key)
    if not existing:
        return []
    return json.loads(existing)
