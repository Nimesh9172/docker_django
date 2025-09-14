# chat/redis_client.py
import redis
from django.conf import settings

r = redis.Redis(
    host=settings.REDIS_CONFIG["HOST"],
    port=settings.REDIS_CONFIG["PORT"],
    db=settings.REDIS_CONFIG["DB"],
    decode_responses=True,  # optional: auto decode bytes → str
)
