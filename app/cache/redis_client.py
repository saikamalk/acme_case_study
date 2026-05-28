import os
import redis
from dotenv import load_dotenv

load_dotenv()
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    decode_responses=True
)
