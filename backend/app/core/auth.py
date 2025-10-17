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
        print(f"DEBUG: Verifying token: {token[:50]}...")  # Log first 50 chars
        # In production, verify with Clerk's JWKS endpoint
        # For now, decode without verification (development only!)
        decoded = jwt.decode(
            token,
            options={"verify_signature": False}  # TODO: Add proper verification
        )
        print(f"DEBUG: Token decoded successfully: {decoded}")
        return decoded
    except jwt.ExpiredSignatureError:
        print(f"DEBUG: Token expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        print(f"DEBUG: Invalid token error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"DEBUG: Unexpected error in token verification: {e}")
        raise HTTPException(status_code=401, detail="Token verification failed")


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
    print(f"DEBUG: get_current_user called with token: {token[:50]}...")
    
    # Development mode: accept test tokens
    if settings.ENVIRONMENT == "development" and token.startswith("test-"):
        print("DEBUG: Using test token")
        return {"sub": "test_user_123"}
    
    user_data = verify_clerk_token(token)
    
    if not user_data.get("sub"):
        print("DEBUG: No 'sub' in user_data")
        raise HTTPException(status_code=401, detail="Invalid user data in token")
    
    print(f"DEBUG: Returning user_data: {user_data}")
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
