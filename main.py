from fastapi import FastAPI
from api.books import router as books_router
from database import client
from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from api.books import router as books_router
from auth.jwt_service import create_access_token, create_refresh_token, verify_refresh_token
from schemas.auth import TokenResponse, RefreshTokenRequest, LoginRequest

# Demo users (in production, use hashed passwords from database)
# For this demo, we use plain passwords - DO NOT USE IN PRODUCTION
DEMO_USERS = {
    "admin": "admin123",
    "user": "user123",
}


def verify_password(plain_password: str, stored_password: str) -> bool:
    """Verify plain password (demo only - NOT FOR PRODUCTION)"""
    return plain_password == stored_password


# FastAPI app
app = FastAPI(
    title="Library API",
    description="A library management API with JWT authentication",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include books router with auth prefix
app.include_router(books_router, prefix="/books", tags=["books"])


@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
async def login(username: str = Form(...), password: str = Form(...)):
    """
    Login endpoint to get access and refresh tokens.
    
    - **username**: Username (demo: "admin" or "user")
    - **password**: Password (demo: "admin123" or "user123")
    """
    # Check if user exists and password is correct
    if username not in DEMO_USERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(password, DEMO_USERS[username]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": username})
    refresh_token = create_refresh_token(data={"sub": username})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@app.post("/auth/refresh", response_model=TokenResponse, tags=["auth"])
async def refresh(request: RefreshTokenRequest):
    """
    Refresh endpoint to get a new access token using a refresh token.
    
    - **refresh_token**: The refresh token received from login
    """
    payload = verify_refresh_token(request.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    # Create new access token
    new_access_token = create_access_token(data={"sub": username})
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=request.refresh_token,
        token_type="bearer"
    )


@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)