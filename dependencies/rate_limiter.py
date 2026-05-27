import time
from typing import Tuple, Dict
import os
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

AUTH_LIMIT = 10
ANON_LIMIT = 2
WINDOW = 60

redis_client = redis.from_url(REDIS_URL, decode_responses=True)


class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client

    def _key(self, identity: str) -> str:
        return f"rate_limit:{identity}"

    async def is_allowed(self, identity: str, limit: int) -> Tuple[bool, Dict]:
        now = int(time.time())
        window_start = now - WINDOW
        key = self._key(identity)

        # clean old requests
        await self.redis.zremrangebyscore(key, 0, window_start)

        count = await self.redis.zcard(key)

        if count >= limit:
            return False, {
                "limit": limit,
                "remaining": 0,
                "reset": WINDOW
            }

        await self.redis.zadd(key, {str(now): now})
        await self.redis.expire(key, WINDOW)

        return True, {
            "limit": limit,
            "remaining": limit - (count + 1),
            "reset": WINDOW
        }


limiter = RateLimiter(redis_client)


async def check_rate_limit(identity: str, is_authenticated: bool):
    limit = AUTH_LIMIT if is_authenticated else ANON_LIMIT
    return await limiter.is_allowed(identity, limit)