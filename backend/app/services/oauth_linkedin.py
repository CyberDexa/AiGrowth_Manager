"""
LinkedIn OAuth 2.0 Service
Handles authentication and token management for LinkedIn API
"""
import httpx
import secrets
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.logging_config import get_logger, log_event

logger = get_logger(__name__)


class LinkedInOAuthService:
    """
    Service for handling LinkedIn OAuth 2.0 authentication
    
    Documentation: https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication
    """
    
    # LinkedIn OAuth endpoints
    AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    PROFILE_URL = "https://api.linkedin.com/v2/userinfo"
    REVOKE_URL = "https://www.linkedin.com/oauth/v2/revoke"
    
    # LinkedIn v2 API endpoints
    ME_URL = "https://api.linkedin.com/v2/me"
    ORGANIZATIONS_URL = "https://api.linkedin.com/v2/organizationalEntityAcls"
    
    # OAuth scopes - Using legacy scopes that work without additional products
    # OpenID Connect scopes (openid, profile, email) require "Sign In with LinkedIn using OpenID Connect" product
    # Legacy scopes work immediately with any LinkedIn app
    SCOPES = [
        "r_liteprofile",    # Legacy: Basic profile info (name, picture)
        "r_emailaddress",   # Legacy: Email address
        # "openid",           # Requires "Sign In with LinkedIn using OpenID Connect" product
        # "profile",          # Requires "Sign In with LinkedIn using OpenID Connect" product
        # "email",            # Requires "Sign In with LinkedIn using OpenID Connect" product
        # "w_member_social",  # Permission to post on behalf of user (requires verification)
        # "r_organization_social",  # Read organization posts (requires verification)
        # "w_organization_social",  # Post as organization (requires verification)
    ]
    
    def __init__(self):
        self.client_id = settings.LINKEDIN_CLIENT_ID
        self.client_secret = settings.LINKEDIN_CLIENT_SECRET
        self.redirect_uri = settings.LINKEDIN_REDIRECT_URI
    
    def generate_state(self) -> str:
        """
        Generate a random state parameter for CSRF protection.
        
        Returns:
            Random 32-character hex string
        """
        return secrets.token_urlsafe(32)
    
    def get_authorization_url(self, state: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate LinkedIn authorization URL with CSRF protection.
        
        Args:
            state: Optional state parameter. If None, generates one.
            
        Returns:
            Tuple of (authorization_url, state_value)
        """
        if state is None:
            state = self.generate_state()
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.SCOPES),
            "state": state,
        }
        
        url = f"{self.AUTH_URL}?{urlencode(params)}"
        logger.info(f"Generated LinkedIn authorization URL with state: {state[:8]}...")
        return url, state
    
    async def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            
        Returns:
            Dict containing:
            - access_token: Bearer token for API requests
            - expires_in: Seconds until token expires (typically 5184000 = 60 days)
            - scope: Granted scopes
            
        Raises:
            httpx.HTTPError: If token exchange fails
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.TOKEN_URL,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                token_data = response.json()
                
                log_event(
                    logger,
                    'oauth_token_exchange',
                    'Successfully exchanged code for LinkedIn token',
                    platform='linkedin',
                    expires_in=token_data.get('expires_in', 0),
                    has_refresh_token=False  # LinkedIn doesn't provide refresh tokens
                )
                return token_data
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to exchange LinkedIn code for token: {e}")
            raise
    
    async def get_user_profile(self, access_token: str) -> Dict:
        """
        Fetch user profile information using access token.
        Uses legacy endpoints for r_liteprofile and r_emailaddress scopes.
        
        Args:
            access_token: LinkedIn access token
            
        Returns:
            Dict containing user profile data:
            - sub: LinkedIn user ID  
            - name: Full name
            - given_name: First name
            - family_name: Last name
            - email: Email address
            - picture: Profile picture URL
            
        Raises:
            httpx.HTTPError: If profile fetch fails
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Fetch basic profile using legacy API
                profile_response = await client.get(
                    self.ME_URL,
                    headers=headers
                )
                profile_response.raise_for_status()
                profile_data = profile_response.json()
                
                # Fetch email separately
                email_response = await client.get(
                    "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
                    headers=headers
                )
                email_response.raise_for_status()
                email_data = email_response.json()
                
                # Extract email
                email = None
                if "elements" in email_data and len(email_data["elements"]) > 0:
                    email = email_data["elements"][0].get("handle~", {}).get("emailAddress")
                
                # Format profile data to match OpenID Connect format
                profile = {
                    "sub": profile_data.get("id"),  # User ID
                    "name": f"{profile_data.get('localizedFirstName', '')} {profile_data.get('localizedLastName', '')}".strip(),
                    "given_name": profile_data.get("localizedFirstName"),
                    "family_name": profile_data.get("localizedLastName"),
                    "email": email,
                    "picture": None  # Profile picture requires additional API call
                }
                
                logger.info(f"Successfully fetched LinkedIn profile for user: {profile.get('sub', 'unknown')}")
                return profile
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch LinkedIn profile: {e}")
            raise
    
    async def get_organization_access(self, access_token: str) -> list:
        """
        Fetch organizations the user can post on behalf of.
        
        Args:
            access_token: LinkedIn access token
            
        Returns:
            List of organization details with IDs and permissions
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Get organizations where user has admin access
                response = await client.get(
                    f"{self.ORGANIZATIONS_URL}?q=roleAssignee",
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                organizations = data.get("elements", [])
                logger.info(f"Found {len(organizations)} LinkedIn organizations for user")
                return organizations
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch LinkedIn organizations: {e}")
            return []
    
    async def revoke_token(self, access_token: str) -> bool:
        """
        Revoke an access token.
        
        Args:
            access_token: LinkedIn access token to revoke
            
        Returns:
            True if revocation successful, False otherwise
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "token": access_token
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.REVOKE_URL,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                
                logger.info("Successfully revoked LinkedIn access token")
                return True
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to revoke LinkedIn token: {e}")
            return False
    
    async def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh an expired access token using refresh token.
        
        Note: LinkedIn's OAuth 2.0 does not provide refresh tokens by default.
        Access tokens are long-lived (60 days). Users must re-authenticate after expiration.
        
        Args:
            refresh_token: Refresh token (not available for LinkedIn)
            
        Returns:
            Dict containing new access_token
            
        Raises:
            NotImplementedError: LinkedIn doesn't support refresh tokens
        """
        logger.warning("Attempted to refresh LinkedIn token - not supported, re-authentication required")
        raise NotImplementedError(
            "LinkedIn access tokens are long-lived (60 days). "
            "Re-authentication required after expiration."
        )
    
    def calculate_token_expiry(self, expires_in: int) -> datetime:
        """
        Calculate token expiration datetime.
        
        Args:
            expires_in: Seconds until token expires
            
        Returns:
            Datetime when token will expire (typically 60 days from now)
        """
        expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        logger.debug(f"LinkedIn token will expire at: {expiry.isoformat()}")
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
            logger.info(f"LinkedIn token expired or expiring soon (expires at {expires_at.isoformat()})")
        
        return is_expired


# Global instance
linkedin_oauth = LinkedInOAuthService()
