"""
Token encryption utilities for secure OAuth token storage
"""
from cryptography.fernet import Fernet
from app.core.config import settings


class TokenEncryption:
    """
    Handles encryption and decryption of OAuth access tokens
    using Fernet symmetric encryption
    """
    
    def __init__(self):
        # Get encryption key from settings
        # If not set, generate one (for development only)
        key = getattr(settings, 'ENCRYPTION_KEY', None)
        if not key:
            # Generate a key for development
            # In production, this should be set in environment variables
            key = Fernet.generate_key()
            print(f"⚠️  WARNING: Using generated encryption key. Set ENCRYPTION_KEY in .env")
            print(f"Generated key: {key.decode()}")
        
        # Ensure key is bytes
        if isinstance(key, str):
            key = key.encode()
        
        self.cipher = Fernet(key)
    
    def encrypt(self, token: str) -> str:
        """
        Encrypt a token string
        
        Args:
            token: Plain text token to encrypt
            
        Returns:
            Encrypted token as string
        """
        if not token:
            return ""
        
        # Convert to bytes and encrypt
        token_bytes = token.encode()
        encrypted_bytes = self.cipher.encrypt(token_bytes)
        
        # Return as string for database storage
        return encrypted_bytes.decode()
    
    def decrypt(self, encrypted_token: str) -> str:
        """
        Decrypt an encrypted token
        
        Args:
            encrypted_token: Encrypted token string
            
        Returns:
            Decrypted token as plain text
        """
        if not encrypted_token:
            return ""
        
        # Convert to bytes and decrypt
        encrypted_bytes = encrypted_token.encode()
        decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
        
        # Return as string
        return decrypted_bytes.decode()


# Global instance
encryption = TokenEncryption()


def encrypt_token(token: str) -> str:
    """Helper function to encrypt a token"""
    return encryption.encrypt(token)


def decrypt_token(encrypted_token: str) -> str:
    """Helper function to decrypt a token"""
    return encryption.decrypt(encrypted_token)
