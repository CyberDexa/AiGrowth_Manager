"""
Meta (Facebook/Instagram) OAuth Service

This module handles OAuth 2.0 authentication for Meta platforms (Facebook and Instagram).

Key Differences from Twitter/LinkedIn:
- Uses standard OAuth 2.0 (no PKCE required)
- Three token types: short-lived (1h) → long-lived (60 days) → Page tokens (never expire)
- Requires Facebook Page selection
- Instagram posting requires linked Instagram Business account

Token Flow:
1. User authorizes app → Get short-lived user token (1 hour)
2. Exchange for long-lived user token (60 days)
3. Get user's Facebook Pages
4. User selects a Page
5. Get Page Access Token (never expires!)
6. Check if Page has Instagram Business account linked
7. Store tokens → Ready to publish
"""

from typing import Dict, Any, Optional, List, Tuple
import httpx
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlencode

from app.core.config import settings
from app.core.logging_config import get_logger, log_event

logger = get_logger(__name__)


class MetaOAuthService:
    """Service for handling Meta OAuth 2.0 authentication"""
    
    # Meta OAuth URLs
    AUTH_URL = "https://www.facebook.com/v18.0/dialog/oauth"
    TOKEN_URL = "https://graph.facebook.com/v18.0/oauth/access_token"
    GRAPH_API_BASE = "https://graph.facebook.com/v18.0"
    
    # Required permissions
    SCOPES = [
        "pages_show_list",         # See list of Pages
        "pages_read_engagement",   # Read Page engagement data
        "pages_manage_posts",      # Create, edit, and delete Page posts
        "instagram_basic",         # Get Instagram account info
        "instagram_content_publish" # Publish Instagram posts
    ]
    
    def __init__(self):
        """Initialize Meta OAuth service with settings from config"""
        self.client_id = settings.META_APP_ID
        self.client_secret = settings.META_APP_SECRET
        self.redirect_uri = settings.META_REDIRECT_URI
        logger.debug("Initialized MetaOAuthService")
    
    def generate_state(self) -> str:
        """
        Generate cryptographically secure random state for CSRF protection
        
        Returns:
            Random state string (32 bytes URL-safe)
        """
        return secrets.token_urlsafe(32)
    
    def get_authorization_url(self, state: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate Meta OAuth authorization URL
        
        Args:
            state: Random state string for CSRF protection (optional, will be generated)
            
        Returns:
            Tuple of (authorization_url, state)
        """
        # Generate state if not provided
        if not state:
            state = self.generate_state()
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "scope": ",".join(self.SCOPES),
            "response_type": "code"
        }
        
        auth_url = f"{self.AUTH_URL}?{urlencode(params)}"
        logger.info(f"Generated Meta authorization URL with state: {state[:8]}...")
        
        return auth_url, state
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for short-lived access token
        
        Args:
            code: Authorization code from callback
            
        Returns:
            Dict containing:
            - access_token: Short-lived user access token (1 hour)
            - token_type: "bearer"
            - expires_in: Token expiration in seconds (3600)
            
        Raises:
            httpx.HTTPError: If token exchange fails
        """
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.TOKEN_URL, params=params)
                response.raise_for_status()
                
                data = response.json()
                expires_in = data.get("expires_in", 3600)
                logger.info(f"Successfully exchanged code for Meta short-lived token (expires in {expires_in}s)")
                
                return {
                    "access_token": data["access_token"],
                    "token_type": data.get("token_type", "bearer"),
                    "expires_in": expires_in
                }
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to exchange Meta code for token: {e}")
            raise
    
    async def exchange_for_long_lived_token(self, short_lived_token: str) -> Dict[str, Any]:
        """
        Exchange short-lived token for long-lived user access token
        
        Args:
            short_lived_token: Short-lived user access token (1 hour)
            
        Returns:
            Dict containing:
            - access_token: Long-lived user access token (60 days)
            - token_type: "bearer"
            - expires_in: Token expiration in seconds (5184000 = 60 days)
            
        Raises:
            httpx.HTTPError: If token exchange fails
        """
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "fb_exchange_token": short_lived_token
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.TOKEN_URL, params=params)
                response.raise_for_status()
                
                data = response.json()
                expires_in = data.get("expires_in", 5184000)
                logger.info(f"Successfully exchanged for Meta long-lived token (expires in {expires_in}s = ~60 days)")
                
                return {
                    "access_token": data["access_token"],
                    "token_type": data.get("token_type", "bearer"),
                    "expires_in": expires_in
                }
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to exchange for Meta long-lived token: {e}")
            raise
    
    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """
        Get authenticated user's Facebook profile
        
        Args:
            access_token: User access token
            
        Returns:
            Dict containing:
            - id: User's Facebook ID
            - name: User's full name
            - email: User's email (if granted)
            
        Raises:
            httpx.HTTPError: If profile fetch fails
        """
        url = f"{self.GRAPH_API_BASE}/me"
        params = {
            "fields": "id,name,email",
            "access_token": access_token
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                user_name = data.get("name", "Unknown")
                user_id = data.get("id", "unknown")
                logger.info(f"Retrieved Meta profile for {user_name} (ID: {user_id})")
                
                return {
                    "id": data["id"],
                    "name": data.get("name"),
                    "email": data.get("email")
                }
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch Meta user profile: {e}")
            raise
    
    async def get_user_pages(self, access_token: str) -> List[Dict[str, Any]]:
        """
        Get list of Facebook Pages the user manages
        
        Args:
            access_token: User access token
            
        Returns:
            List of dicts, each containing:
            - id: Page ID
            - name: Page name
            - access_token: Page access token (never expires!)
            - category: Page category
            - tasks: List of tasks user can perform on Page
            
        Raises:
            httpx.HTTPError: If request fails
        """
        url = f"{self.GRAPH_API_BASE}/me/accounts"
        params = {
            "fields": "id,name,access_token,category,tasks",
            "access_token": access_token
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                pages = data.get("data", [])
                
                logger.info(f"Retrieved {len(pages)} Facebook Pages")
                return pages
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch Meta user pages: {e}")
            raise
    
    async def get_page_instagram_account(
        self, 
        page_id: str, 
        page_access_token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check if a Facebook Page has a linked Instagram Business account
        
        Args:
            page_id: Facebook Page ID
            page_access_token: Page access token
            
        Returns:
            Dict containing Instagram account info if linked, None otherwise:
            - id: Instagram Business account ID
            - username: Instagram username
            - profile_picture_url: Profile picture URL (optional)
            
        Raises:
            httpx.HTTPError: If request fails
        """
        url = f"{self.GRAPH_API_BASE}/{page_id}"
        params = {
            "fields": "instagram_business_account{id,username,profile_picture_url}",
            "access_token": page_access_token
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                instagram_account = data.get("instagram_business_account")
                
                if instagram_account:
                    username = instagram_account.get("username", "unknown")
                    logger.info(f"Found Instagram account: @{username}")
                    return {
                        "id": instagram_account["id"],
                        "username": username,
                        "profile_picture_url": instagram_account.get("profile_picture_url")
                    }
                else:
                    logger.info("No Instagram Business account linked to this Page")
                    return None
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch Instagram account for Page {page_id}: {e}")
            raise
    
    async def get_page_access_token(
        self,
        page_id: str,
        user_access_token: str
    ) -> str:
        """
        Get Page Access Token for a specific Facebook Page
        
        Note: Page Access Tokens do NOT expire (unless explicitly invalidated)
        
        Args:
            page_id: Facebook Page ID
            user_access_token: User's long-lived access token
            
        Returns:
            Page access token (never expires)
            
        Raises:
            httpx.HTTPError: If request fails
        """
        url = f"{self.GRAPH_API_BASE}/{page_id}"
        params = {
            "fields": "access_token",
            "access_token": user_access_token
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                page_token = data["access_token"]
                
                logger.info(f"Retrieved Page Access Token for Page {page_id}")
                return page_token
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to get Page Access Token for Page {page_id}: {e}")
            raise
    
    async def verify_page_permissions(
        self,
        page_id: str,
        page_access_token: str
    ) -> Dict[str, bool]:
        """
        Verify what permissions the app has for a Facebook Page
        
        Args:
            page_id: Facebook Page ID
            page_access_token: Page access token
            
        Returns:
            Dict with permission status:
            - can_post: Whether app can create posts
            - can_publish: Whether app can publish content
            
        Raises:
            httpx.HTTPError: If request fails
        """
        url = f"{self.GRAPH_API_BASE}/{page_id}"
        params = {
            "fields": "tasks",
            "access_token": page_access_token
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                tasks = data.get("tasks", [])
                
                permissions = {
                    "can_post": "CREATE_CONTENT" in tasks or "MANAGE" in tasks,
                    "can_publish": "MANAGE" in tasks
                }
                
                logger.info(f"Page {page_id} permissions: {permissions}")
                return permissions
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to verify permissions for Page {page_id}: {e}")
            raise
    
    def calculate_token_expiry(self, expires_in: int) -> datetime:
        """
        Calculate token expiration datetime
        
        Args:
            expires_in: Token lifetime in seconds
            
        Returns:
            Expiration datetime
        """
        expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        logger.debug(f"Meta token will expire at: {expiry.isoformat()}")
        return expiry
    
    def is_token_expired(self, expires_at: datetime) -> bool:
        """
        Check if a token has expired.
        
        Args:
            expires_at: Token expiration datetime
            
        Returns:
            True if token has expired or will expire within 24 hours
        """
        # Consider token expired if less than 24 hours remaining
        buffer = timedelta(hours=24)
        is_expired = datetime.utcnow() + buffer >= expires_at
        
        if is_expired:
            logger.info(f"Meta token expired or expiring soon (expires at {expires_at.isoformat()})")
        
        return is_expired
    
    async def revoke_token(self, access_token: str) -> bool:
        """
        Revoke a user access token
        
        Args:
            access_token: Token to revoke
            
        Returns:
            True if revocation successful
            
        Raises:
            httpx.HTTPError: If revocation fails
        """
        url = f"{self.GRAPH_API_BASE}/me/permissions"
        params = {"access_token": access_token}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, params=params)
                response.raise_for_status()
                logger.info("Successfully revoked Meta access token")
                return True
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to revoke Meta token: {e}")
            return False


# Global instance
meta_oauth = MetaOAuthService()
