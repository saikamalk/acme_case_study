import json
import os

from app.cache.redis_client import redis_client

SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS"))

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
    redis_client.set(key,json.dumps(history), ex=SESSION_TTL_SECONDS)


def get_conversation_history(username: str):
    key = f"session:{username}"
    existing = redis_client.get(key)
    if not existing:
        return []
    return json.loads(existing)

def clear_conversation_history(username: str):
    key = f"session:{username}"
    redis_client.delete(key)
    if redis_client.exists(key) == 0:
        return "Conversation history cleared"
    return "Conversation history not cleared"