from fastapi import FastAPI, HTTPException, status, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi
from api.books import router as books_router
from auth.jwt_service import create_access_token, create_refresh_token, verify_refresh_token, verify_token
from schemas.auth import TokenResponse, RefreshTokenRequest, LoginRequest
from pydantic import BaseModel

# Request schemas for signup
class SignupRequest(BaseModel):
    username: str
    password: str

class SignupResponse(BaseModel):
    message: str
    username: str

# In-memory user storage (use database in production)
users_db: dict = {
    "admin": "admin123",
    "user": "user123",
}

security = HTTPBearer(description="JWT Token")


def verify_password(plain_password: str, stored_password: str) -> bool:
    """Verify plain password (demo only - NOT FOR PRODUCTION)"""
    return plain_password == stored_password


# FastAPI app
app = FastAPI(
    title="Library API",
    description="A library management API with JWT authentication",
    version="1.0.0"
)

# Rate limiting middleware is disabled
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    return await call_next(request)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(books_router, prefix="/books", tags=["books"])

def custom_openapi():
    """Custom OpenAPI schema to include Bearer token security"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Library API",
        version="1.0.0",
        description="A library management API with JWT authentication",
        routes=app.routes,
    )
    
    # Add bearer token security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token from /auth/login endpoint"
        }
    }
    
    for path, path_item in openapi_schema["paths"].items():
        for method, operation in path_item.items():
            if isinstance(operation, dict):
                # Застосовуємо Bearer токен для всіх методів з тегом "books"
                if "tags" in operation and "books" in operation["tags"]:
                    operation["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.post("/auth/signup", response_model=SignupResponse, tags=["auth"])
async def signup(request: SignupRequest):
    """
    Register a new user account.
    
    - username: Username (must be unique)
    - password: Password (minimum 3 characters)
    """
    # Validate input
    if len(request.username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters"
        )
    
    if len(request.password) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 3 characters"
        )
    
    # Check if user already exists
    if request.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    
    # Register new user
    users_db[request.username] = request.password
    
    return SignupResponse(
        message="User registered successfully",
        username=request.username
    )


@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
async def login(username: str = Form(...), password: str = Form(...)):
    """
    Login endpoint to get access and refresh tokens.
    
    - username: Username
    - password: Password
    """
    # Check if user exists and password is correct
    if username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(password, users_db[username]):
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
    
    - refresh_token: The refresh token received from login
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
