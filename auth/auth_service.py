import os
from datetime import timedelta
from typing import Optional
from flask_jwt_extended import create_access_token, create_refresh_token
from bson import ObjectId

class AuthService:
    """Service for managing authentication tokens"""
    
    def __init__(self, db):
        self.db = db
        self.users_collection = db["users"]
        
    async def create_tokens(self, user_id: str, username: str) -> dict:
        """Create access and refresh tokens for a user"""
        
        # Access token expires in 15 minutes
        access_token = create_access_token(
            identity=str(user_id),
            additional_claims={"username": username},
            expires_delta=timedelta(minutes=15)
        )
        
        # Refresh token expires in 7 days
        refresh_token = create_refresh_token(
            identity=str(user_id),
            additional_claims={"username": username},
            expires_delta=timedelta(days=7)
        )
        
        # Store refresh token in database for invalidation support
        await self.store_refresh_token(user_id, refresh_token)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
        }
    
    async def store_refresh_token(self, user_id: str, refresh_token: str) -> None:
        """Store refresh token in database"""
        await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "refresh_tokens": refresh_token
                }
            },
            upsert=True
        )
    
    async def validate_user(self, username: str, password: str) -> Optional[str]:
        """Validate user credentials and return user_id"""
        user = await self.users_collection.find_one({"username": username})
        
        if user and user.get("password") == password:  # In production, use bcrypt!
            return str(user["_id"])
        
        return None
    
    async def register_user(self, username: str, password: str) -> dict:
        """Register a new user"""
        existing_user = await self.users_collection.find_one({"username": username})
        
        if existing_user:
            return {"error": "User already exists"}
        
        result = await self.users_collection.insert_one({
            "username": username,
            "password": password,  # In production, use bcrypt!
            "refresh_tokens": None
        })
        
        return {"user_id": str(result.inserted_id), "username": username}
    
    async def revoke_refresh_token(self, user_id: str) -> None:
        """Revoke refresh token (logout)"""
        await self.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"refresh_tokens": None}}
        )
