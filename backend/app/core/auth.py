"""
Authentication utilities for verifying Clerk JWT tokens
"""
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional

from app.core.config import settings

security = HTTPBearer()


def verify_clerk_token(token: str) -> dict:
    """
    Verify Clerk JWT token and return decoded payload
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        Decoded token payload with user info
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # In production, verify with Clerk's JWKS endpoint
        # For now, decode without verification (development only!)
        decoded = jwt.decode(
            token,
            options={"verify_signature": False}  # TODO: Add proper verification
        )
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    FastAPI dependency to get current authenticated user from JWT token
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user_id": user["sub"]}
    """
    token = credentials.credentials
    user_data = verify_clerk_token(token)
    
    if not user_data.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid user data in token")
    
    return user_data


async def get_current_user_id(
    user: dict = Security(get_current_user)
) -> str:
    """
    FastAPI dependency to get just the user ID (Clerk ID)
    
    Usage:
        @app.get("/me")
        async def get_me(user_id: str = Depends(get_current_user_id)):
            return {"user_id": user_id}
    """
    return user["sub"]
