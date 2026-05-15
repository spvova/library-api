# dependencies.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from auth.auth_service import verify_token
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    payload = verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload["sub"]

# optional variant: returns username or None (useful for rate limiter)
async def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[str]:
    if not token:
        return None
    payload = verify_token(token, token_type="access")
    return payload["sub"] if payload else None
