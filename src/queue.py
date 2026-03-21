import json
import os
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_KEY = os.getenv("QUEUE_KEY", "bm:incoming")

_r = redis.from_url(REDIS_URL, decode_responses=True)

def enqueue_incoming(job: dict):
    _r.lpush(QUEUE_KEY, json.dumps(job, ensure_ascii=False))

def dequeue_incoming(block_seconds: int = 10) -> dict | None:
    item = _r.brpop(QUEUE_KEY, timeout=block_seconds)
    if not item:
        return None
    _, raw = item
    return json.loads(raw)
