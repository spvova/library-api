# dependencies/rate_limiter.py
import time
from fastapi import Request, HTTPException, Depends
from typing import Optional
from redis_client import redis_client
from dependencies import get_current_user_optional

# ліміти: (requests, period_seconds)
RATE_LIMITS = {
    "authenticated": (10, 60),
    "anonymous": (2, 60),
}

async def rate_limit(request: Request, user_id: Optional[str] = Depends(get_current_user_optional)):
    identity = user_id or request.client.host
    limit_type = "authenticated" if user_id else "anonymous"
    limit, period = RATE_LIMITS[limit_type]

    key = f"rate_limit:{limit_type}:{identity}:{request.url.path}"

    now = int(time.time())
    window_start = now - period

    r = redis_client

    # Видаляємо старі записи
    await r.zremrangebyscore(key, min=0, max=window_start)

    # Підрахунок запитів у вікні
    request_count = await r.zcard(key)

    if request_count >= limit:
        # можна додати заголовки Retry-After
        raise HTTPException(status_code=429, detail="Too many requests")

    # Додаємо поточний запит
    # використовуємо score = now, member = f"{now}:{unique}"
    member = f"{now}:{request.client.host}:{request.headers.get('user-agent','')}"
    await r.zadd(key, {member: now})
    await r.expire(key, period)
