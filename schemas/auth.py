from pydantic import BaseModel, Field
from typing import Optional


class TokenResponse(BaseModel):
    """Response with access and refresh tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Request to refresh the access token"""
    refresh_token: str


class LoginRequest(BaseModel):
    """Login credentials"""
    username: str = Field(..., description="Username for login")
    password: str = Field(..., description="Password for login")


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # subject (username)
    type: Optional[str] = "access"
