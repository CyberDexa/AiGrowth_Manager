"""
Social Media OAuth API Endpoints
Handles OAuth flows for LinkedIn, Twitter, and Meta
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List
import secrets
from datetime import datetime

from app.db.database import get_db
from app.core.auth import get_current_user
from app.models.social_account import SocialAccount
from app.models.business import Business
from app.schemas.social import SocialAccountResponse
from app.services.oauth_linkedin import linkedin_oauth
from app.services.oauth_twitter import twitter_oauth
from app.services.oauth_meta import MetaOAuthService
from app.core.encryption import encrypt_token, decrypt_token
from app.core.config import settings

router = APIRouter(prefix="/social", tags=["social"])


# ============================================================================
# HELPER: PKCE State Management (for Twitter OAuth)
# ============================================================================
# For MVP, we'll store PKCE state in memory. Production should use Redis.
_pkce_state_store = {}  # {state: {"code_verifier": "...", "business_id": 123}}


def store_pkce_state(state: str, code_verifier: str, business_id: int):
    """Store PKCE code_verifier with state token (in-memory for MVP)"""
    _pkce_state_store[state] = {
        "code_verifier": code_verifier,
        "business_id": business_id
    }


def retrieve_pkce_state(state: str) -> dict:
    """Retrieve and remove PKCE state (one-time use)"""
    return _pkce_state_store.pop(state, None)


# ============================================================================
# LINKEDIN OAUTH ENDPOINTS
# ============================================================================

@router.get("/linkedin/auth")
async def linkedin_auth_init(
    business_id: int = Query(..., description="Business ID to connect account to"),
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate LinkedIn OAuth flow
    
    Steps:
    1. Verify business belongs to user
    2. Generate random state token
    3. Store state in session/cache (TODO: implement)
    4. Redirect to LinkedIn authorization URL
    """
    user_id = user_data.get("sub")
    
    # Verify business belongs to user
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # TODO: Store state in Redis with business_id for verification in callback
    # For now, we'll include business_id in state (not secure for production!)
    state_with_business = f"{state}:{business_id}"
    
    # Get authorization URL
    auth_url = linkedin_oauth.get_authorization_url(state_with_business)
    
    # Redirect user to LinkedIn
    return RedirectResponse(url=auth_url)


@router.get("/linkedin/callback")
async def linkedin_auth_callback(
    code: str = Query(None, description="Authorization code from LinkedIn"),
    state: str = Query(None, description="State token for CSRF protection"),
    error: str = Query(None, description="Error from LinkedIn"),
    error_description: str = Query(None, description="Error description"),
    db: Session = Depends(get_db)
):
    """
    Handle LinkedIn OAuth callback
    
    Steps:
    1. Verify state token (CSRF protection)
    2. Exchange code for access token
    3. Fetch user profile
    4. Store encrypted token in database
    5. Redirect user back to settings page
    """
    # Handle errors from LinkedIn
    if error:
        # Redirect back to settings with error message
        frontend_url = "http://localhost:3000/dashboard/settings?tab=social&error=" + error
        return RedirectResponse(url=frontend_url)
    
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")
    
    # Extract business_id from state (insecure, for MVP only)
    try:
        state_token, business_id_str = state.split(":")
        business_id = int(business_id_str)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # TODO: Verify state token against stored value in Redis
    
    try:
        # Exchange code for access token
        token_data = await linkedin_oauth.exchange_code_for_token(code)
        access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in", 5184000)  # Default 60 days
        
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")
        
        # Fetch user profile
        profile = await linkedin_oauth.get_user_profile(access_token)
        
        # Extract profile data
        linkedin_user_id = profile.get("sub")  # OpenID Connect 'sub' claim
        name = profile.get("name", "")
        email = profile.get("email", "")
        
        if not linkedin_user_id:
            raise HTTPException(status_code=400, detail="Could not get LinkedIn user ID")
        
        # Calculate token expiry
        token_expires_at = linkedin_oauth.calculate_token_expiry(expires_in)
        
        # Encrypt access token before storing
        encrypted_token = encrypt_token(access_token)
        
        # Check if account already exists
        existing_account = db.query(SocialAccount).filter(
            SocialAccount.business_id == business_id,
            SocialAccount.platform == "linkedin"
        ).first()
        
        if existing_account:
            # Update existing account
            existing_account.platform_user_id = linkedin_user_id
            existing_account.platform_username = name or email
            existing_account.access_token = encrypted_token
            existing_account.token_expires_at = token_expires_at
            existing_account.is_active = True
        else:
            # Create new account
            new_account = SocialAccount(
                business_id=business_id,
                platform="linkedin",
                platform_user_id=linkedin_user_id,
                platform_username=name or email,
                access_token=encrypted_token,
                token_expires_at=token_expires_at,
                is_active=True
            )
            db.add(new_account)
        
        db.commit()
        
        # Redirect back to settings page with success message
        frontend_url = "http://localhost:3000/dashboard/settings?tab=social&success=linkedin"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        # Log error and redirect with error message
        print(f"LinkedIn OAuth error: {str(e)}")
        frontend_url = f"http://localhost:3000/dashboard/settings?tab=social&error=auth_failed"
        return RedirectResponse(url=frontend_url)


@router.post("/linkedin/disconnect")
async def linkedin_disconnect(
    business_id: int = Query(..., description="Business ID"),
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disconnect LinkedIn account
    
    Marks the account as inactive (soft delete)
    """
    user_id = user_data.get("sub")
    
    # Verify business belongs to user
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Find LinkedIn account
    account = db.query(SocialAccount).filter(
        SocialAccount.business_id == business_id,
        SocialAccount.platform == "linkedin"
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="LinkedIn account not connected")
    
    # Soft delete - mark as inactive
    account.is_active = False
    db.commit()
    
    return {"message": "LinkedIn account disconnected successfully"}


# ============================================================================
# GENERAL ENDPOINTS
# ============================================================================

@router.get("/accounts", response_model=List[SocialAccountResponse])
async def get_social_accounts(
    business_id: int = Query(..., description="Business ID"),
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all connected social accounts for a business
    
    Returns list of accounts without sensitive token data
    """
    user_id = user_data.get("sub")
    
    # Verify business belongs to user
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Get all active social accounts
    accounts = db.query(SocialAccount).filter(
        SocialAccount.business_id == business_id,
        SocialAccount.is_active == True
    ).all()
    
    return accounts


# ============================================================================
# TWITTER OAUTH ENDPOINTS (with PKCE)
# ============================================================================

@router.get("/twitter/auth")
async def twitter_auth_init(
    business_id: int = Query(..., description="Business ID to connect account to"),
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate Twitter OAuth flow with PKCE
    
    Steps:
    1. Verify business belongs to user
    2. Generate random state token
    3. Generate PKCE code_verifier and code_challenge
    4. Store code_verifier with state (for callback verification)
    5. Redirect to Twitter authorization URL with code_challenge
    """
    user_id = user_data.get("sub")
    
    # Verify business belongs to user
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Generate PKCE code_verifier and code_challenge
    code_verifier = twitter_oauth.generate_code_verifier()
    code_challenge = twitter_oauth.generate_code_challenge(code_verifier)
    
    # Store code_verifier with state for callback verification
    # In production, use Redis with TTL (10 minutes)
    store_pkce_state(state, code_verifier, business_id)
    
    # Get authorization URL with code_challenge
    auth_url = twitter_oauth.get_authorization_url(state, code_challenge)
    
    # Redirect user to Twitter
    return RedirectResponse(url=auth_url)


@router.get("/twitter/callback")
async def twitter_auth_callback(
    code: str = Query(None, description="Authorization code from Twitter"),
    state: str = Query(None, description="State token for CSRF protection"),
    error: str = Query(None, description="Error from Twitter"),
    error_description: str = Query(None, description="Error description"),
    db: Session = Depends(get_db)
):
    """
    Handle Twitter OAuth callback with PKCE
    
    Steps:
    1. Verify state token (CSRF protection)
    2. Retrieve code_verifier from storage
    3. Exchange code + code_verifier for access token and refresh token
    4. Fetch user profile
    5. Store encrypted tokens in database
    6. Redirect user back to settings page
    """
    # Handle errors from Twitter
    if error:
        frontend_url = "http://localhost:3000/dashboard/settings?tab=social&error=" + error
        return RedirectResponse(url=frontend_url)
    
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")
    
    # Retrieve PKCE state
    pkce_data = retrieve_pkce_state(state)
    if not pkce_data:
        raise HTTPException(status_code=400, detail="Invalid or expired state parameter")
    
    code_verifier = pkce_data["code_verifier"]
    business_id = pkce_data["business_id"]
    
    try:
        # Exchange code + code_verifier for tokens
        token_data = await twitter_oauth.exchange_code_for_token(code, code_verifier)
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")  # Twitter provides refresh tokens!
        expires_in = token_data.get("expires_in", 7200)  # Default 2 hours
        
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")
        
        # Fetch user profile
        profile = await twitter_oauth.get_user_profile(access_token)
        
        # Extract profile data
        twitter_user_id = profile.get("id")
        username = profile.get("username")  # @handle without @
        name = profile.get("name", "")
        
        if not twitter_user_id or not username:
            raise HTTPException(status_code=400, detail="Could not get Twitter user data")
        
        # Calculate token expiry
        token_expires_at = twitter_oauth.calculate_token_expiry(expires_in)
        
        # Encrypt tokens before storing
        encrypted_access_token = encrypt_token(access_token)
        encrypted_refresh_token = encrypt_token(refresh_token) if refresh_token else None
        
        # Check if account already exists
        existing_account = db.query(SocialAccount).filter(
            SocialAccount.business_id == business_id,
            SocialAccount.platform == "twitter"
        ).first()
        
        if existing_account:
            # Update existing account
            existing_account.platform_user_id = twitter_user_id
            existing_account.platform_username = username
            existing_account.access_token = encrypted_access_token
            existing_account.refresh_token = encrypted_refresh_token
            existing_account.token_expires_at = token_expires_at
            existing_account.is_active = True
        else:
            # Create new account
            new_account = SocialAccount(
                business_id=business_id,
                platform="twitter",
                platform_user_id=twitter_user_id,
                platform_username=username,
                access_token=encrypted_access_token,
                refresh_token=encrypted_refresh_token,
                token_expires_at=token_expires_at,
                is_active=True
            )
            db.add(new_account)
        
        db.commit()
        
        # Redirect back to settings page with success message
        frontend_url = "http://localhost:3000/dashboard/settings?tab=social&success=twitter"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        # Log error and redirect with error message
        print(f"Twitter OAuth error: {str(e)}")
        frontend_url = f"http://localhost:3000/dashboard/settings?tab=social&error=auth_failed"
        return RedirectResponse(url=frontend_url)


@router.post("/twitter/disconnect")
async def twitter_disconnect(
    business_id: int = Query(..., description="Business ID"),
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disconnect Twitter account
    
    Optionally revokes the access token on Twitter's side,
    then marks the account as inactive (soft delete)
    """
    user_id = user_data.get("sub")
    
    # Verify business belongs to user
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Find Twitter account
    account = db.query(SocialAccount).filter(
        SocialAccount.business_id == business_id,
        SocialAccount.platform == "twitter"
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Twitter account not connected")
    
    # Check if token is expired before attempting revocation
    token_expired = False
    if account.token_expires_at:
        token_expired = datetime.utcnow() > account.token_expires_at
    
    # Only attempt revocation if token is not expired
    if not token_expired and account.access_token:
        try:
            decrypted_token = decrypt_token(account.access_token)
            await twitter_oauth.revoke_token(decrypted_token, "access_token")
        except Exception as e:
            print(f"Error revoking Twitter token: {e}")
            # Continue with disconnect even if revocation fails
    
    # Soft delete - mark as inactive
    account.is_active = False
    db.commit()
    
    return {"message": "Twitter account disconnected successfully"}


# ============================================================================
# META (FACEBOOK/INSTAGRAM) OAUTH ENDPOINTS
# ============================================================================

@router.get("/meta/auth")
async def meta_auth_init(
    business_id: int = Query(..., description="Business ID to connect account to"),
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate Meta (Facebook/Instagram) OAuth flow
    
    Steps:
    1. Verify business belongs to user
    2. Generate random state token
    3. Redirect to Facebook authorization URL
    4. After auth, user will select Facebook Page
    """
    user_id = user_data.get("sub")
    
    # Verify business belongs to user
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state with business_id for callback verification
    # Format: "state:business_id" (for MVP; production should use Redis)
    state_with_business = f"{state}:{business_id}"
    
    # Initialize Meta OAuth service
    meta_oauth = MetaOAuthService(
        client_id=settings.META_APP_ID,
        client_secret=settings.META_APP_SECRET,
        redirect_uri=settings.META_REDIRECT_URI
    )
    
    # Get authorization URL
    auth_url = meta_oauth.get_authorization_url(state_with_business)
    
    # Redirect user to Facebook
    return RedirectResponse(url=auth_url)


@router.get("/meta/callback")
async def meta_auth_callback(
    code: str = Query(None, description="Authorization code from Facebook"),
    state: str = Query(None, description="State token for CSRF protection"),
    error: str = Query(None, description="Error from Facebook"),
    error_description: str = Query(None, description="Error description"),
    db: Session = Depends(get_db)
):
    """
    Handle Meta OAuth callback
    
    Steps:
    1. Exchange code for short-lived token
    2. Exchange short-lived for long-lived token (60 days)
    3. Get user profile
    4. Get user's Facebook Pages
    5. Store token temporarily, return pages list for user to select
    """
    # Handle errors
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"Meta OAuth error: {error} - {error_description}"
        )
    
    if not code or not state:
        raise HTTPException(
            status_code=400,
            detail="Missing authorization code or state"
        )
    
    # Extract business_id from state
    try:
        state_token, business_id = state.rsplit(":", 1)
        business_id = int(business_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Verify business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Initialize Meta OAuth service
    meta_oauth = MetaOAuthService(
        client_id=settings.META_APP_ID,
        client_secret=settings.META_APP_SECRET,
        redirect_uri=settings.META_REDIRECT_URI
    )
    
    try:
        # Step 1: Exchange code for short-lived token
        short_token_data = await meta_oauth.exchange_code_for_token(code)
        short_token = short_token_data["access_token"]
        
        # Step 2: Exchange for long-lived token (60 days)
        long_token_data = await meta_oauth.exchange_for_long_lived_token(short_token)
        long_lived_token = long_token_data["access_token"]
        expires_in = long_token_data["expires_in"]
        
        # Step 3: Get user profile
        user_profile = await meta_oauth.get_user_profile(long_lived_token)
        
        # Step 4: Get user's Facebook Pages
        pages = await meta_oauth.get_user_pages(long_lived_token)
        
        if not pages:
            raise HTTPException(
                status_code=400,
                detail="No Facebook Pages found. Please create a Facebook Page first."
            )
        
        # Store token and pages temporarily in _pkce_state_store for page selection
        # (In production, use Redis with expiry)
        temp_state = secrets.token_urlsafe(32)
        _pkce_state_store[temp_state] = {
            "business_id": business_id,
            "user_id": user_profile["id"],
            "user_name": user_profile.get("name"),
            "long_lived_token": long_lived_token,
            "expires_in": expires_in,
            "pages": pages
        }
        
        # Redirect to frontend page selection page
        frontend_url = settings.FRONTEND_URL
        redirect_url = f"{frontend_url}/dashboard/settings?tab=social&meta_state={temp_state}"
        
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete Meta OAuth: {str(e)}"
        )


@router.get("/meta/pages")
async def get_meta_pages(
    temp_state: str = Query(..., description="Temporary state token"),
    user_data: dict = Depends(get_current_user)
):
    """
    Get list of Facebook Pages for user to select from
    
    Called after OAuth callback redirects to frontend
    """
    # Retrieve temp data (but don't pop it yet - we need it for select-page)
    temp_data = _pkce_state_store.get(temp_state)
    if not temp_data:
        raise HTTPException(status_code=400, detail="Invalid or expired state. Please reconnect Facebook.")
    
    return {
        "pages": temp_data.get("pages", []),
        "user_name": temp_data.get("user_name")
    }


@router.post("/meta/select-page")
async def meta_select_page(
    page_id: str,
    temp_state: str,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    User selects which Facebook Page to connect
    
    Steps:
    1. Retrieve temp OAuth data from state
    2. Get Page Access Token for selected page
    3. Check for Instagram Business account
    4. Store all data in database
    """
    # Retrieve temp data
    temp_data = _pkce_state_store.pop(temp_state, None)
    if not temp_data:
        raise HTTPException(status_code=400, detail="Invalid or expired state")
    
    business_id = temp_data["business_id"]
    user_id = user_data.get("sub")
    
    # Verify business belongs to user
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Find selected page in pages list
    selected_page = next(
        (p for p in temp_data["pages"] if p["id"] == page_id),
        None
    )
    
    if not selected_page:
        raise HTTPException(status_code=400, detail="Invalid page selection")
    
    # Initialize Meta OAuth service
    meta_oauth = MetaOAuthService(
        client_id=settings.META_APP_ID,
        client_secret=settings.META_APP_SECRET,
        redirect_uri=settings.META_REDIRECT_URI
    )
    
    try:
        # Get Page Access Token (never expires!)
        page_token = selected_page.get("access_token")
        
        # Check for Instagram Business account
        instagram_account = await meta_oauth.get_page_instagram_account(
            page_id=page_id,
            page_access_token=page_token
        )
        
        # Calculate token expiry (60 days from now)
        token_expiry = meta_oauth.calculate_token_expiry(temp_data["expires_in"])
        
        # Check if account already exists
        existing = db.query(SocialAccount).filter(
            SocialAccount.business_id == business_id,
            SocialAccount.platform == "facebook"
        ).first()
        
        if existing:
            # Update existing account
            existing.platform_user_id = temp_data["user_id"]
            existing.platform_username = temp_data["user_name"]
            existing.access_token = encrypt_token(temp_data["long_lived_token"])
            existing.token_expires_at = token_expiry
            existing.page_id = page_id
            existing.page_name = selected_page.get("name")
            existing.page_access_token = encrypt_token(page_token)
            existing.instagram_account_id = instagram_account.get("id") if instagram_account else None
            existing.instagram_username = instagram_account.get("username") if instagram_account else None
            existing.is_active = True
            
            db.commit()
            db.refresh(existing)
            
            return {
                "message": "Facebook Page updated successfully",
                "account_id": existing.id,
                "page_name": selected_page.get("name"),
                "instagram_connected": instagram_account is not None,
                "instagram_username": instagram_account.get("username") if instagram_account else None
            }
        else:
            # Create new account
            account = SocialAccount(
                business_id=business_id,
                platform="facebook",
                platform_user_id=temp_data["user_id"],
                platform_username=temp_data["user_name"],
                access_token=encrypt_token(temp_data["long_lived_token"]),
                token_expires_at=token_expiry,
                page_id=page_id,
                page_name=selected_page.get("name"),
                page_access_token=encrypt_token(page_token),
                instagram_account_id=instagram_account.get("id") if instagram_account else None,
                instagram_username=instagram_account.get("username") if instagram_account else None,
                is_active=True
            )
            
            db.add(account)
            db.commit()
            db.refresh(account)
            
            return {
                "message": "Facebook Page connected successfully",
                "account_id": account.id,
                "page_name": selected_page.get("name"),
                "instagram_connected": instagram_account is not None,
                "instagram_username": instagram_account.get("username") if instagram_account else None
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect Facebook Page: {str(e)}"
        )


@router.post("/meta/disconnect")
async def meta_disconnect(
    business_id: int = Query(..., description="Business ID"),
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disconnect Meta (Facebook/Instagram) account
    
    Marks the account as inactive (soft delete)
    """
    user_id = user_data.get("sub")
    
    # Verify business belongs to user
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Find Facebook/Meta account (handle both platform names)
    account = db.query(SocialAccount).filter(
        SocialAccount.business_id == business_id,
        SocialAccount.platform.in_(["facebook", "meta"])
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Meta account not connected")
    
    # Soft delete - mark as inactive
    account.is_active = False
    db.commit()
    
    return {"message": "Meta account disconnected successfully"}
