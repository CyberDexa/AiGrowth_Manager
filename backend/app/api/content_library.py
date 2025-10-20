"""
Content Library API Endpoints
Save and reuse successful posts
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import Optional, List
from datetime import datetime

from app.db.database import get_db
from app.core.auth import get_current_user
from app.models.content import Content
from app.models.published_post import PublishedPost
from pydantic import BaseModel

router = APIRouter(prefix="/content-library", tags=["content-library"])


# ============================================
# SCHEMAS
# ============================================

class LibraryItemBase(BaseModel):
    id: int
    source: str  # 'content' or 'published_post'
    platform: str
    text: str
    hashtags: Optional[str] = None
    media_urls: Optional[List[str]] = None
    saved_at: datetime
    created_at: datetime
    
    # Engagement metrics (for published posts)
    likes_count: Optional[int] = None
    comments_count: Optional[int] = None
    shares_count: Optional[int] = None
    impressions_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class LibraryListResponse(BaseModel):
    items: List[LibraryItemBase]
    total: int
    page: int
    page_size: int


class SaveToLibraryRequest(BaseModel):
    source: str  # 'content' or 'published_post'
    item_id: int


class SaveToLibraryResponse(BaseModel):
    success: bool
    message: str
    item: LibraryItemBase


class RemoveFromLibraryResponse(BaseModel):
    success: bool
    message: str


# ============================================
# HELPER FUNCTIONS
# ============================================

def content_to_library_item(content: Content) -> LibraryItemBase:
    """Convert Content model to LibraryItemBase"""
    return LibraryItemBase(
        id=content.id,
        source="content",
        platform=content.platform.value,
        text=content.text,
        hashtags=content.hashtags,
        media_urls=content.media_urls.split(',') if content.media_urls else None,
        saved_at=content.library_saved_at or content.created_at,
        created_at=content.created_at,
        likes_count=None,
        comments_count=None,
        shares_count=None,
        impressions_count=None
    )


def published_post_to_library_item(post: PublishedPost) -> LibraryItemBase:
    """Convert PublishedPost model to LibraryItemBase"""
    return LibraryItemBase(
        id=post.id,
        source="published_post",
        platform=post.platform,
        text=post.content_text,
        hashtags=None,  # Published posts don't have separate hashtags field
        media_urls=post.content_images,
        saved_at=post.library_saved_at or post.created_at,
        created_at=post.created_at,
        likes_count=post.likes_count,
        comments_count=post.comments_count,
        shares_count=post.shares_count,
        impressions_count=post.impressions_count
    )


# ============================================
# ENDPOINTS
# ============================================

@router.post("/save", response_model=SaveToLibraryResponse)
def save_to_library(
    request: SaveToLibraryRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a content item or published post to the library
    
    - **source**: Either 'content' or 'published_post'
    - **item_id**: ID of the item to save
    """
    try:
        user_id = current_user["sub"]
        
        if request.source == "content":
            # Find the content item
            item = db.query(Content).filter(
                Content.id == request.item_id
            ).first()
            
            if not item:
                raise HTTPException(status_code=404, detail="Content not found")
            
            # Verify ownership through business
            if item.business.user_id != user_id:
                raise HTTPException(status_code=403, detail="Not authorized to save this content")
            
            # Save to library
            item.saved_to_library = True
            item.library_saved_at = datetime.utcnow()
            db.commit()
            db.refresh(item)
            
            return SaveToLibraryResponse(
                success=True,
                message="Content saved to library",
                item=content_to_library_item(item)
            )
            
        elif request.source == "published_post":
            # Find the published post
            item = db.query(PublishedPost).filter(
                PublishedPost.id == request.item_id
            ).first()
            
            if not item:
                raise HTTPException(status_code=404, detail="Published post not found")
            
            # Verify ownership through business
            if item.business.user_id != user_id:
                raise HTTPException(status_code=403, detail="Not authorized to save this post")
            
            # Save to library
            item.saved_to_library = True
            item.library_saved_at = datetime.utcnow()
            db.commit()
            db.refresh(item)
            
            return SaveToLibraryResponse(
                success=True,
                message="Post saved to library",
                item=published_post_to_library_item(item)
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid source. Must be 'content' or 'published_post'")
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save to library: {str(e)}")


@router.get("", response_model=LibraryListResponse)
def list_library_items(
    business_id: int = Query(..., description="Business ID"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    search: Optional[str] = Query(None, description="Search in text"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all saved library items for a business
    
    - **business_id**: ID of the business
    - **platform**: Filter by platform (optional)
    - **search**: Search in content text (optional)
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    """
    try:
        user_id = current_user["sub"]
        
        # Build queries for both tables
        content_query = db.query(Content).filter(
            and_(
                Content.business_id == business_id,
                Content.saved_to_library == True
            )
        )
        
        posts_query = db.query(PublishedPost).filter(
            and_(
                PublishedPost.business_id == business_id,
                PublishedPost.saved_to_library == True
            )
        )
        
        # Apply platform filter
        if platform:
            content_query = content_query.filter(Content.platform == platform)
            posts_query = posts_query.filter(PublishedPost.platform == platform)
        
        # Apply search filter
        if search:
            content_query = content_query.filter(Content.text.ilike(f"%{search}%"))
            posts_query = posts_query.filter(PublishedPost.content_text.ilike(f"%{search}%"))
        
        # Get all items
        content_items = content_query.all()
        published_items = posts_query.all()
        
        # Convert to library items
        all_items = []
        for item in content_items:
            all_items.append(content_to_library_item(item))
        for item in published_items:
            all_items.append(published_post_to_library_item(item))
        
        # Sort by saved_at descending
        all_items.sort(key=lambda x: x.saved_at, reverse=True)
        
        # Calculate pagination
        total = len(all_items)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = all_items[start_idx:end_idx]
        
        return LibraryListResponse(
            items=paginated_items,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list library items: {str(e)}")


@router.delete("/{source}/{item_id}", response_model=RemoveFromLibraryResponse)
def remove_from_library(
    source: str,
    item_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove an item from the library (doesn't delete the item, just unsaves it)
    
    - **source**: Either 'content' or 'published_post'
    - **item_id**: ID of the item to remove
    """
    try:
        user_id = current_user["sub"]
        
        if source == "content":
            item = db.query(Content).filter(Content.id == item_id).first()
            
            if not item:
                raise HTTPException(status_code=404, detail="Content not found")
            
            # Verify ownership
            if item.business.user_id != user_id:
                raise HTTPException(status_code=403, detail="Not authorized")
            
            item.saved_to_library = False
            item.library_saved_at = None
            
        elif source == "published_post":
            item = db.query(PublishedPost).filter(PublishedPost.id == item_id).first()
            
            if not item:
                raise HTTPException(status_code=404, detail="Published post not found")
            
            # Verify ownership
            if item.business.user_id != user_id:
                raise HTTPException(status_code=403, detail="Not authorized")
            
            item.saved_to_library = False
            item.library_saved_at = None
        else:
            raise HTTPException(status_code=400, detail="Invalid source")
        
        db.commit()
        
        return RemoveFromLibraryResponse(
            success=True,
            message="Item removed from library"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to remove from library: {str(e)}")


@router.get("/stats")
def get_library_stats(
    business_id: int = Query(..., description="Business ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics about the content library
    
    - **business_id**: ID of the business
    """
    try:
        # Count items by source
        content_count = db.query(Content).filter(
            and_(
                Content.business_id == business_id,
                Content.saved_to_library == True
            )
        ).count()
        
        posts_count = db.query(PublishedPost).filter(
            and_(
                PublishedPost.business_id == business_id,
                PublishedPost.saved_to_library == True
            )
        ).count()
        
        # Count by platform
        platform_counts = {}
        
        # Content platforms
        from sqlalchemy import func
        content_platforms = db.query(
            Content.platform,
            func.count(Content.id)
        ).filter(
            and_(
                Content.business_id == business_id,
                Content.saved_to_library == True
            )
        ).group_by(Content.platform).all()
        
        for platform, count in content_platforms:
            platform_counts[platform.value] = platform_counts.get(platform.value, 0) + count
        
        # Published post platforms
        post_platforms = db.query(
            PublishedPost.platform,
            func.count(PublishedPost.id)
        ).filter(
            and_(
                PublishedPost.business_id == business_id,
                PublishedPost.saved_to_library == True
            )
        ).group_by(PublishedPost.platform).all()
        
        for platform, count in post_platforms:
            platform_counts[platform] = platform_counts.get(platform, 0) + count
        
        return {
            "total_items": content_count + posts_count,
            "ai_generated_count": content_count,
            "published_count": posts_count,
            "by_platform": platform_counts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get library stats: {str(e)}")
