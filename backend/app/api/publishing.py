"""
Publishing API Endpoints

API routes for publishing content to social media platforms.
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.auth import get_current_user_id
from app.models.business import Business
from app.models.social_account import SocialAccount
from app.models.published_post import PublishedPost
from app.schemas.publishing import (
    PublishRequest,
    PublishResponse,
    PublishedPostResponse,
    PublishedPostListResponse
)
from app.services.publishing_linkedin import (
    LinkedInPublishingService,
    LinkedInAPIError,
    TokenExpiredError,
    RateLimitError
)
from app.services.publishing_twitter import (
    TwitterPublishingService,
    TwitterAPIError,
    TokenExpiredError as TwitterTokenExpiredError,
    RateLimitError as TwitterRateLimitError,
    DuplicateTweetError,
    PartialThreadError
)
from app.services.publishing_meta import MetaPublishingService
from app.core.encryption import decrypt_token
from app.services.oauth_twitter import twitter_oauth

router = APIRouter()


@router.post("/publishing/linkedin", response_model=PublishResponse)
async def publish_to_linkedin(
    request: PublishRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Publish content to LinkedIn.
    
    - Validates business ownership
    - Gets active LinkedIn account
    - Posts to LinkedIn API
    - Stores published post record
    """
    # Verify business ownership
    business = db.query(Business).filter(
        Business.id == request.business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Get active LinkedIn account for this business
    linkedin_account = db.query(SocialAccount).filter(
        SocialAccount.business_id == request.business_id,
        SocialAccount.platform == "linkedin",
        SocialAccount.is_active == True
    ).first()
    
    if not linkedin_account:
        raise HTTPException(
            status_code=400,
            detail="No connected LinkedIn account found. Please connect your LinkedIn account first."
        )
    
    # Check if token is expired
    if linkedin_account.token_expires_at and linkedin_account.token_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=401,
            detail="LinkedIn token expired. Please reconnect your LinkedIn account."
        )
    
    # Create published_post record (status: pending)
    published_post = PublishedPost(
        business_id=request.business_id,
        strategy_id=request.strategy_id,
        social_account_id=linkedin_account.id,
        content_text=request.content_text,
        content_images=request.content_images,
        content_links=request.content_links,
        platform="linkedin",
        status="scheduled" if request.scheduled_for else "pending",
        scheduled_for=request.scheduled_for
    )
    
    db.add(published_post)
    db.commit()
    db.refresh(published_post)
    
    # If scheduled for future, return early
    if request.scheduled_for:
        return PublishResponse(
            id=published_post.id,
            business_id=published_post.business_id,
            platform=published_post.platform,
            status=published_post.status,
            content_text=published_post.content_text,
            scheduled_for=published_post.scheduled_for,
            created_at=published_post.created_at
        )
    
    # Publish immediately
    try:
        async with LinkedInPublishingService() as linkedin_service:
            result = await linkedin_service.post_to_linkedin(
                account=linkedin_account,
                content_text=request.content_text,
                content_images=request.content_images,
                content_links=request.content_links
            )
        
        # Update published_post with success
        published_post.status = "published"
        published_post.platform_post_id = result["platform_post_id"]
        published_post.platform_post_url = result["platform_post_url"]
        published_post.published_at = result["published_at"]
        
        db.commit()
        db.refresh(published_post)
        
        return PublishResponse(
            id=published_post.id,
            business_id=published_post.business_id,
            platform=published_post.platform,
            status=published_post.status,
            content_text=published_post.content_text,
            platform_post_id=published_post.platform_post_id,
            platform_post_url=published_post.platform_post_url,
            published_at=published_post.published_at,
            created_at=published_post.created_at
        )
    
    except TokenExpiredError as e:
        # Token expired - update post status
        published_post.status = "failed"
        published_post.error_message = "LinkedIn token expired. Please reconnect your account."
        db.commit()
        
        raise HTTPException(
            status_code=401,
            detail="LinkedIn token expired. Please reconnect your LinkedIn account."
        )
    
    except RateLimitError as e:
        # Rate limit - update post status
        published_post.status = "failed"
        published_post.error_message = str(e)
        db.commit()
        
        raise HTTPException(
            status_code=429,
            detail="LinkedIn rate limit exceeded. Please try again later."
        )
    
    except LinkedInAPIError as e:
        # Other LinkedIn API error
        published_post.status = "failed"
        published_post.error_message = str(e)
        db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish to LinkedIn: {str(e)}"
        )
    
    except Exception as e:
        # Unexpected error
        published_post.status = "failed"
        published_post.error_message = f"Unexpected error: {str(e)}"
        db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while publishing: {str(e)}"
        )


@router.post("/publishing/twitter", response_model=PublishResponse)
async def publish_to_twitter(
    request: PublishRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Publish content to Twitter/X.
    
    - Validates business ownership
    - Gets active Twitter account
    - Auto-detects single tweet vs thread based on content length
    - Refreshes token if expired (Twitter supports refresh tokens!)
    - Posts to Twitter API v2
    - Stores published post record with thread info
    """
    # Verify business ownership
    business = db.query(Business).filter(
        Business.id == request.business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Get active Twitter account for this business
    twitter_account = db.query(SocialAccount).filter(
        SocialAccount.business_id == request.business_id,
        SocialAccount.platform == "twitter",
        SocialAccount.is_active == True
    ).first()
    
    if not twitter_account:
        raise HTTPException(
            status_code=400,
            detail="No connected Twitter account found. Please connect your Twitter account first."
        )
    
    # Check if token needs refresh (Twitter tokens expire after 2 hours)
    if twitter_account.token_expires_at:
        if twitter_oauth.should_refresh_token(twitter_account.token_expires_at):
            # Token expired or about to expire - refresh it!
            try:
                if not twitter_account.refresh_token:
                    raise HTTPException(
                        status_code=401,
                        detail="Twitter token expired and no refresh token available. Please reconnect."
                    )
                
                # Decrypt refresh token
                from app.core.encryption import decrypt_token, encrypt_token
                decrypted_refresh_token = decrypt_token(twitter_account.refresh_token)
                
                # Get new access token
                token_data = await twitter_oauth.refresh_access_token(decrypted_refresh_token)
                new_access_token = token_data.get("access_token")
                new_refresh_token = token_data.get("refresh_token")  # Twitter returns new refresh token!
                expires_in = token_data.get("expires_in", 7200)
                
                # Update stored tokens
                twitter_account.access_token = encrypt_token(new_access_token)
                if new_refresh_token:
                    twitter_account.refresh_token = encrypt_token(new_refresh_token)
                twitter_account.token_expires_at = twitter_oauth.calculate_token_expiry(expires_in)
                db.commit()
                
            except Exception as e:
                raise HTTPException(
                    status_code=401,
                    detail=f"Failed to refresh Twitter token: {str(e)}. Please reconnect your account."
                )
    
    # Create published_post record (status: pending)
    published_post = PublishedPost(
        business_id=request.business_id,
        strategy_id=request.strategy_id,
        social_account_id=twitter_account.id,
        content_text=request.content_text,
        content_images=request.content_images,
        content_links=request.content_links,
        platform="twitter",
        status="scheduled" if request.scheduled_for else "pending",
        scheduled_for=request.scheduled_for
    )
    
    db.add(published_post)
    db.commit()
    db.refresh(published_post)
    
    # If scheduled for future, return early
    if request.scheduled_for:
        return PublishResponse(
            id=published_post.id,
            business_id=published_post.business_id,
            platform=published_post.platform,
            status=published_post.status,
            content_text=published_post.content_text,
            scheduled_for=published_post.scheduled_for,
            created_at=published_post.created_at
        )
    
    # Publish immediately
    try:
        async with TwitterPublishingService() as twitter_service:
            result = await twitter_service.post_to_twitter(
                account=twitter_account,
                content_text=request.content_text,
                use_premium_limit=False  # MVP: assume standard 280-char limit
            )
        
        # Update published_post with success
        published_post.status = "published"
        published_post.platform_post_id = result["platform_post_id"]  # First tweet ID
        published_post.platform_post_url = result["platform_post_url"]
        published_post.published_at = result["published_at"]
        
        # Store thread info if it's a thread
        thread_tweet_ids = result.get("thread_tweet_ids", [])
        if len(thread_tweet_ids) > 1:
            # Store thread IDs as JSON (or in metadata field)
            import json
            published_post.error_message = json.dumps({
                "thread": True,
                "tweet_ids": thread_tweet_ids,
                "tweet_count": len(thread_tweet_ids)
            })
        
        db.commit()
        db.refresh(published_post)
        
        return PublishResponse(
            id=published_post.id,
            business_id=published_post.business_id,
            platform=published_post.platform,
            status=published_post.status,
            content_text=published_post.content_text,
            platform_post_id=published_post.platform_post_id,
            platform_post_url=published_post.platform_post_url,
            published_at=published_post.published_at,
            created_at=published_post.created_at
        )
    
    except PartialThreadError as e:
        # Thread partially posted - save what we have
        published_post.status = "partial"
        published_post.platform_post_id = e.tweet_ids[0] if e.tweet_ids else None
        published_post.platform_post_url = e.first_tweet_url
        published_post.error_message = str(e)
        db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Thread partially posted: {str(e)}"
        )
    
    except DuplicateTweetError as e:
        # Duplicate tweet
        published_post.status = "failed"
        published_post.error_message = "Duplicate tweet"
        db.commit()
        
        raise HTTPException(
            status_code=400,
            detail="This tweet appears to be a duplicate"
        )
    
    except TwitterTokenExpiredError as e:
        # Token expired (shouldn't happen after refresh attempt)
        published_post.status = "failed"
        published_post.error_message = "Twitter token expired"
        db.commit()
        
        raise HTTPException(
            status_code=401,
            detail="Twitter token expired. Please reconnect your account."
        )
    
    except TwitterRateLimitError as e:
        # Rate limit
        published_post.status = "failed"
        published_post.error_message = str(e)
        db.commit()
        
        raise HTTPException(
            status_code=429,
            detail="Twitter rate limit exceeded. Please try again later."
        )
    
    except TwitterAPIError as e:
        # Other Twitter API error
        published_post.status = "failed"
        published_post.error_message = str(e)
        db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish to Twitter: {str(e)}"
        )
    
    except Exception as e:
        # Unexpected error
        published_post.status = "failed"
        published_post.error_message = f"Unexpected error: {str(e)}"
        db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while publishing: {str(e)}"
        )


@router.get("/publishing/posts", response_model=PublishedPostListResponse)
async def get_published_posts(
    business_id: int = Query(..., description="Business ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get list of published posts for a business.
    
    Supports filtering by status and platform, with pagination.
    """
    # Verify business ownership
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Build query
    query = db.query(PublishedPost).filter(
        PublishedPost.business_id == business_id
    )
    
    # Apply filters
    if status:
        query = query.filter(PublishedPost.status == status)
    
    if platform:
        query = query.filter(PublishedPost.platform == platform)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    posts = query.order_by(PublishedPost.created_at.desc()).offset(offset).limit(limit).all()
    
    return PublishedPostListResponse(
        posts=[PublishedPostResponse.from_orm(post) for post in posts],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/publishing/posts/{post_id}", response_model=PublishedPostResponse)
async def get_published_post(
    post_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get a single published post by ID."""
    post = db.query(PublishedPost).filter(PublishedPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Published post not found")
    
    # Verify business ownership
    business = db.query(Business).filter(
        Business.id == post.business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return PublishedPostResponse.from_orm(post)


@router.post("/publishing/posts/{post_id}/retry", response_model=PublishResponse)
async def retry_failed_post(
    post_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Retry publishing a failed post.
    
    Only works for posts with status='failed'.
    """
    post = db.query(PublishedPost).filter(PublishedPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Published post not found")
    
    # Verify business ownership
    business = db.query(Business).filter(
        Business.id == post.business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if post can be retried
    if post.status != "failed":
        raise HTTPException(
            status_code=400,
            detail=f"Can only retry failed posts. Current status: {post.status}"
        )
    
    # Get social account
    social_account = db.query(SocialAccount).filter(
        SocialAccount.id == post.social_account_id
    ).first()
    
    if not social_account or not social_account.is_active:
        raise HTTPException(
            status_code=400,
            detail="Social account is no longer active. Please reconnect."
        )
    
    # Update retry tracking
    post.retry_count += 1
    post.last_retry_at = datetime.utcnow()
    post.status = "pending"
    db.commit()
    
    # Retry publishing
    try:
        async with LinkedInPublishingService() as linkedin_service:
            result = await linkedin_service.post_to_linkedin(
                account=social_account,
                content_text=post.content_text,
                content_images=post.content_images,
                content_links=post.content_links
            )
        
        # Update with success
        post.status = "published"
        post.platform_post_id = result["platform_post_id"]
        post.platform_post_url = result["platform_post_url"]
        post.published_at = result["published_at"]
        post.error_message = None
        
        db.commit()
        db.refresh(post)
        
        return PublishResponse(
            id=post.id,
            business_id=post.business_id,
            platform=post.platform,
            status=post.status,
            content_text=post.content_text,
            platform_post_id=post.platform_post_id,
            platform_post_url=post.platform_post_url,
            published_at=post.published_at,
            created_at=post.created_at
        )
    
    except Exception as e:
        # Retry failed
        post.status = "failed"
        post.error_message = str(e)
        db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Retry failed: {str(e)}"
        )


# ============================================================================
# META (FACEBOOK/INSTAGRAM) PUBLISHING ENDPOINTS
# ============================================================================

@router.post("/publishing/facebook", response_model=PublishResponse)
async def publish_to_facebook(
    request: PublishRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Publish content to Facebook Page
    
    Args:
        request: Publish request with business_id and content
        
    Returns:
        PublishResponse with post details
    """
    # Verify business belongs to user
    business = db.query(Business).filter(
        Business.id == request.business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Get Facebook account
    facebook_account = db.query(SocialAccount).filter(
        SocialAccount.business_id == request.business_id,
        SocialAccount.platform == "facebook",
        SocialAccount.is_active == True
    ).first()
    
    if not facebook_account:
        raise HTTPException(
            status_code=404, 
            detail="Facebook account not connected. Please connect your Facebook Page first."
        )
    
    if not facebook_account.page_id or not facebook_account.page_access_token:
        raise HTTPException(
            status_code=400,
            detail="Facebook Page not configured. Please reconnect your account."
        )
    
    # Decrypt tokens
    page_access_token = decrypt_token(facebook_account.page_access_token)
    
    # Initialize publishing service
    meta_service = MetaPublishingService()
    
    # Validate content length
    is_valid, error_msg = meta_service.validate_content_length(request.content_text, "facebook")
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Get image URL from images list if provided
    image_url = request.content_images[0] if request.content_images else None
    link_url = request.content_links[0] if request.content_links else None
    
    try:
        # Publish to Facebook
        result = await meta_service.post_to_facebook(
            page_id=facebook_account.page_id,
            page_access_token=page_access_token,
            content=request.content_text,
            image_url=image_url,
            link=link_url
        )
        
        # Save to database
        published_post = PublishedPost(
            business_id=request.business_id,
            social_account_id=facebook_account.id,
            platform="facebook",
            content=request.content_text,
            platform_post_id=result["id"],
            platform_post_url=result.get("url"),
            status="published",
            published_at=datetime.utcnow()
        )
        
        db.add(published_post)
        db.commit()
        db.refresh(published_post)
        
        return PublishResponse(
            success=True,
            message="Successfully published to Facebook",
            post_id=published_post.id,
            platform="facebook",
            platform_post_id=result["id"],
            platform_post_url=result.get("url"),
            published_at=published_post.published_at,
            created_at=published_post.created_at
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Save failed post to database
        published_post = PublishedPost(
            business_id=request.business_id,
            social_account_id=facebook_account.id,
            platform="facebook",
            content=request.content_text,
            status="failed",
            error_message=str(e)
        )
        db.add(published_post)
        db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish to Facebook: {str(e)}"
        )


@router.post("/publishing/instagram", response_model=PublishResponse)
async def publish_to_instagram(
    request: PublishRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Publish content to Instagram Business account
    
    Args:
        request: Publish request with business_id, content, and image_url (REQUIRED)
        
    Returns:
        PublishResponse with post details
        
    Note: Instagram requires an image_url. Text-only posts are not supported.
    """
    # Verify business belongs to user
    business = db.query(Business).filter(
        Business.id == request.business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Get Facebook account (Instagram is linked through Facebook Page)
    facebook_account = db.query(SocialAccount).filter(
        SocialAccount.business_id == request.business_id,
        SocialAccount.platform == "facebook",
        SocialAccount.is_active == True
    ).first()
    
    if not facebook_account:
        raise HTTPException(
            status_code=404, 
            detail="Facebook account not connected. Connect Facebook first to access Instagram."
        )
    
    if not facebook_account.instagram_account_id:
        raise HTTPException(
            status_code=400,
            detail="Instagram Business account not linked. Please link your Instagram account to your Facebook Page."
        )
    
    if not facebook_account.page_access_token:
        raise HTTPException(
            status_code=400,
            detail="Page access token missing. Please reconnect your Facebook account."
        )
    
    # Validate image_url is provided
    image_url = request.content_images[0] if request.content_images else None
    if not image_url:
        raise HTTPException(
            status_code=400,
            detail="Instagram posts require an image. Please provide an image in content_images."
        )
    
    # Decrypt tokens
    page_access_token = decrypt_token(facebook_account.page_access_token)
    
    # Initialize publishing service
    meta_service = MetaPublishingService()
    
    # Validate content length
    is_valid, error_msg = meta_service.validate_content_length(request.content_text, "instagram")
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    try:
        # Publish to Instagram (two-step process)
        result = await meta_service.post_to_instagram(
            instagram_account_id=facebook_account.instagram_account_id,
            page_access_token=page_access_token,
            content=request.content_text,
            image_url=image_url
        )
        
        # Save to database
        published_post = PublishedPost(
            business_id=request.business_id,
            social_account_id=facebook_account.id,
            platform="instagram",
            content=request.content_text,
            platform_post_id=result["id"],
            platform_post_url=result.get("url"),
            status="published",
            published_at=datetime.utcnow()
        )
        
        db.add(published_post)
        db.commit()
        db.refresh(published_post)
        
        return PublishResponse(
            success=True,
            message=f"Successfully published to Instagram @{facebook_account.instagram_username}",
            post_id=published_post.id,
            platform="instagram",
            platform_post_id=result["id"],
            platform_post_url=result.get("url"),
            published_at=published_post.published_at,
            created_at=published_post.created_at
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Save failed post to database
        published_post = PublishedPost(
            business_id=request.business_id,
            social_account_id=facebook_account.id,
            platform="instagram",
            content=request.content_text,
            status="failed",
            error_message=str(e)
        )
        db.add(published_post)
        db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish to Instagram: {str(e)}"
        )

