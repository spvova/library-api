# auth/routes.py
from fastapi import APIRouter, HTTPException
from auth.schemas import LoginRequest, TokenResponse
from auth.auth_service import create_access_token, create_refresh_token, verify_token

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    # TODO: замінити на перевірку в БД
    if data.username != "admin" or data.password != "password":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_access_token({"sub": data.username})
    refresh = create_refresh_token({"sub": data.username})
    return TokenResponse(access_token=access, refresh_token=refresh)

@router.post("/refresh")
async def refresh(refresh_token: str):
    payload = verify_token(refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    new_access = create_access_token({"sub": payload["sub"]})
    return {"access_token": new_access}
