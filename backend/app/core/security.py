"""
Security utilities for OAuth and token management
Handles encryption, state validation, and secure token storage
"""
import secrets
import json
from typing import Optional, Dict
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Import Redis client (will fallback to in-memory if Redis unavailable)
try:
    from app.core.redis_client import get_redis_client
    REDIS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Redis not available, using in-memory state storage: {e}")
    REDIS_AVAILABLE = False


class TokenEncryption:
    """
    Handles encryption and decryption of OAuth tokens
    Uses Fernet (symmetric encryption) for secure token storage
    """
    
    def __init__(self):
        """Initialize Fernet cipher with encryption key from settings"""
        if not settings.ENCRYPTION_KEY:
            logger.warning("ENCRYPTION_KEY not set - generating temporary key (NOT FOR PRODUCTION!)")
            self.cipher_suite = Fernet(Fernet.generate_key())
        else:
            # Ensure the key is properly formatted
            try:
                self.cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode())
            except Exception as e:
                logger.error(f"Invalid ENCRYPTION_KEY format: {e}")
                raise ValueError("ENCRYPTION_KEY must be a valid Fernet key. Generate with: Fernet.generate_key()")
    
    def encrypt_token(self, token: str) -> str:
        """
        Encrypt a token for secure storage
        
        Args:
            token: Plain text token
            
        Returns:
            Encrypted token (base64 encoded)
        """
        try:
            encrypted = self.cipher_suite.encrypt(token.encode())
            logger.debug("Successfully encrypted token")
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Failed to encrypt token: {e}")
            raise
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """
        Decrypt a token for use
        
        Args:
            encrypted_token: Encrypted token (base64 encoded)
            
        Returns:
            Plain text token
        """
        try:
            decrypted = self.cipher_suite.decrypt(encrypted_token.encode())
            logger.debug("Successfully decrypted token")
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt token: {e}")
            raise
    
    def encrypt_if_present(self, token: Optional[str]) -> Optional[str]:
        """
        Encrypt token if present, otherwise return None
        
        Args:
            token: Optional plain text token
            
        Returns:
            Encrypted token or None
        """
        return self.encrypt_token(token) if token else None
    
    def decrypt_if_present(self, encrypted_token: Optional[str]) -> Optional[str]:
        """
        Decrypt token if present, otherwise return None
        
        Args:
            encrypted_token: Optional encrypted token
            
        Returns:
            Plain text token or None
        """
        return self.decrypt_token(encrypted_token) if encrypted_token else None


class StateManager:
    """
    Manages OAuth state parameters for CSRF protection
    Uses Redis for production or in-memory dict for development/fallback
    """
    
    def __init__(self):
        """Initialize state storage"""
        self.state_expiry_seconds = 600  # 10 minutes
        
        # Always initialize in-memory storage as fallback
        self._states: Dict[str, Dict] = {}
        
        # Try to use Redis if available
        if REDIS_AVAILABLE:
            try:
                self.redis_client = get_redis_client()
                self.use_redis = True
                logger.info("✅ StateManager using Redis for state storage")
            except Exception as e:
                logger.warning(f"⚠️  Redis unavailable, falling back to in-memory storage: {e}")
                self.use_redis = False
        else:
            self.use_redis = False
            logger.warning("⚠️  StateManager using in-memory storage (NOT RECOMMENDED FOR PRODUCTION)")
    
    def _get_state_key(self, state: str) -> str:
        """Generate Redis key for state."""
        return f"oauth:state:{state}"
    
    def generate_state(self, business_id: int, platform: str, code_verifier: Optional[str] = None) -> str:
        """
        Generate and store a state parameter
        
        Args:
            business_id: Business ID for OAuth connection
            platform: Platform name (linkedin, twitter, meta)
            code_verifier: Optional PKCE code verifier (for Twitter)
            
        Returns:
            Generated state string
        """
        state = secrets.token_urlsafe(32)
        self.store_state(state, business_id, platform, code_verifier)
        return state
    
    def store_state(self, state: str, business_id: int, platform: str, code_verifier: Optional[str] = None) -> None:
        """
        Store an existing state parameter with associated data
        
        Args:
            state: State parameter (usually from OAuth service)
            business_id: Business ID for OAuth connection
            platform: Platform name (linkedin, twitter, meta)
            code_verifier: Optional PKCE code verifier (for Twitter)
        """
        state_data = {
            "business_id": business_id,
            "platform": platform,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(seconds=self.state_expiry_seconds)).isoformat()
        }
        
        if code_verifier:
            state_data["code_verifier"] = code_verifier
        
        # Store in Redis or in-memory
        if self.use_redis:
            try:
                # Store with automatic expiration (TTL)
                self.redis_client.setex(
                    self._get_state_key(state),
                    self.state_expiry_seconds,
                    json.dumps(state_data)
                )
                logger.info(f"Stored state for {platform} OAuth (business_id={business_id}) [Redis]")
            except Exception as e:
                logger.error(f"Failed to store state in Redis: {e}")
                # Fallback to in-memory
                self._states[state] = state_data
                logger.warning("Stored state in memory as fallback")
        else:
            self._states[state] = state_data
            logger.info(f"Stored state for {platform} OAuth (business_id={business_id}) [In-Memory]")
    
    def validate_state(self, state: str, business_id: int, platform: str) -> Dict:
        """
        Validate and retrieve state data
        
        Args:
            state: State parameter from OAuth callback
            business_id: Business ID from callback
            platform: Platform name from callback
            
        Returns:
            State data including code_verifier (if present)
            
        Raises:
            ValueError: If state is invalid, expired, or doesn't match
        """
        state_data = None
        
        # Retrieve from Redis or in-memory
        if self.use_redis:
            try:
                state_key = self._get_state_key(state)
                state_json = self.redis_client.get(state_key)
                
                if not state_json:
                    logger.warning(f"Invalid or expired state parameter: {state[:8]}... [Redis]")
                    raise ValueError("Invalid or expired state parameter")
                
                state_data = json.loads(state_json)
                
                # Delete immediately (one-time use) - Redis DELETE is atomic
                self.redis_client.delete(state_key)
                
            except ValueError:
                raise
            except Exception as e:
                logger.error(f"Failed to retrieve state from Redis: {e}")
                # Try fallback to in-memory
                if state in self._states:
                    state_data = self._states.pop(state)
                else:
                    raise ValueError("Invalid or expired state parameter")
        else:
            # Clean up expired states first (in-memory only)
            self._cleanup_expired_states()
            
            # Check if state exists
            if state not in self._states:
                logger.warning(f"Invalid state parameter: {state[:8]}... [In-Memory]")
                raise ValueError("Invalid or expired state parameter")
            
            state_data = self._states.pop(state)  # Remove immediately (one-time use)
        
        # Validate expiration (double-check even with TTL)
        expires_at = datetime.fromisoformat(state_data["expires_at"])
        if datetime.utcnow() > expires_at:
            logger.warning(f"Expired state parameter: {state[:8]}...")
            raise ValueError("State parameter has expired")
        
        # Validate business_id
        if state_data["business_id"] != business_id:
            logger.warning(f"Business ID mismatch for state: {state[:8]}...")
            raise ValueError("Business ID mismatch")
        
        # Validate platform
        if state_data["platform"] != platform:
            logger.warning(f"Platform mismatch for state: {state[:8]}...")
            raise ValueError("Platform mismatch")
        
        logger.info(f"Successfully validated state for {platform} OAuth (business_id={business_id})")
        return state_data
    
    def validate_state_no_business(self, state: str) -> Dict:
        """
        Validate and retrieve state data without business_id validation.
        This is used in callbacks where business_id comes from the state itself.
        
        Args:
            state: State parameter from OAuth callback
            
        Returns:
            State data including business_id, platform, and code_verifier (if present)
            
        Raises:
            ValueError: If state is invalid or expired
        """
        state_data = None
        
        # Retrieve from Redis or in-memory
        if self.use_redis:
            try:
                state_key = self._get_state_key(state)
                state_json = self.redis_client.get(state_key)
                
                if not state_json:
                    logger.warning(f"Invalid or expired state parameter: {state[:8]}... [Redis]")
                    raise ValueError("Invalid or expired state parameter")
                
                state_data = json.loads(state_json)
                
                # Delete immediately (one-time use) - Redis DELETE is atomic
                self.redis_client.delete(state_key)
                
            except ValueError:
                raise
            except Exception as e:
                logger.error(f"Failed to retrieve state from Redis: {e}")
                # Try fallback to in-memory
                if state in self._states:
                    state_data = self._states.pop(state)
                else:
                    raise ValueError("Invalid or expired state parameter")
        else:
            # Clean up expired states first (in-memory only)
            self._cleanup_expired_states()
            
            # Check if state exists
            if state not in self._states:
                logger.warning(f"Invalid state parameter: {state[:8]}... [In-Memory]")
                raise ValueError("Invalid or expired state parameter")
            
            state_data = self._states.pop(state)  # Remove immediately (one-time use)
        
        # Validate expiration (double-check even with TTL)
        expires_at = datetime.fromisoformat(state_data["expires_at"])
        if datetime.utcnow() > expires_at:
            logger.warning(f"Expired state parameter: {state[:8]}...")
            raise ValueError("State parameter has expired")
        
        business_id = state_data.get("business_id")
        platform = state_data.get("platform")
        logger.info(f"Successfully validated state for {platform} OAuth (business_id={business_id})")
        return state_data
    
    def _cleanup_expired_states(self):
        """Remove expired states from in-memory storage (Redis handles this with TTL)"""
        if self.use_redis:
            return  # Redis TTL handles cleanup automatically
        
        now = datetime.utcnow()
        expired_states = [
            state for state, data in self._states.items()
            if datetime.fromisoformat(data["expires_at"]) < now
        ]
        
        for state in expired_states:
            del self._states[state]
        
        if expired_states:
            logger.debug(f"Cleaned up {len(expired_states)} expired states [In-Memory]")


# Global instances
token_encryption = TokenEncryption()
state_manager = StateManager()


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key
    
    Returns:
        Base64-encoded Fernet key
        
    Usage:
        Run this once to generate a key, then add to .env:
        ENCRYPTION_KEY=<generated_key>
    """
    key = Fernet.generate_key()
    return key.decode()


if __name__ == "__main__":
    # Generate a new encryption key for .env
    print("Generated ENCRYPTION_KEY:")
    print(generate_encryption_key())
    print("\nAdd this to your .env file:")
    print(f"ENCRYPTION_KEY={generate_encryption_key()}")
