"""
Content API endpoints for content generation and management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.db.database import get_db
from app.core.auth import get_current_user_id
from app.models.business import Business
from app.models.content import Content, Platform, ContentType, ContentTone, ContentStatus
from app.services.content_service import content_service

router = APIRouter(prefix="/content", tags=["content"])


# Pydantic schemas
class ContentGenerateRequest(BaseModel):
    business_id: int
    platform: str
    content_type: str = "post"
    tone: str = "professional"
    topic: Optional[str] = None
    additional_context: Optional[str] = None
    num_posts: int = 1


class ContentCreate(BaseModel):
    business_id: int
    platform: str
    content_type: str = "post"
    tone: str = "professional"
    text: str
    hashtags: Optional[str] = None
    scheduled_for: Optional[datetime] = None


class ContentUpdate(BaseModel):
    text: Optional[str] = None
    hashtags: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    status: Optional[str] = None


class ContentResponse(BaseModel):
    id: int
    business_id: int
    platform: str
    content_type: str
    tone: str
    text: str
    hashtags: Optional[str]
    status: str
    scheduled_for: Optional[datetime]
    published_at: Optional[datetime]
    ai_generated: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_content(
    request: ContentGenerateRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate social media content using AI
    """
    # Verify business exists and belongs to user
    business = db.query(Business).filter(
        Business.id == request.business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Generate content using AI
    ai_result = await content_service.generate_content(
        business_name=business.name,
        business_description=business.description or "",
        target_audience=business.target_audience or "General audience",
        platform=request.platform,
        content_type=request.content_type,
        tone=request.tone,
        topic=request.topic,
        additional_context=request.additional_context,
        num_posts=request.num_posts
    )
    
    if not ai_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate content: {ai_result.get('error')}"
        )
    
    return {
        "success": True,
        "content": ai_result["content"],
        "model_used": ai_result["model_used"],
        "tokens_used": ai_result.get("tokens_used", {})
    }


@router.post("/", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    content_data: ContentCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Save generated content to the database
    """
    # Verify business exists and belongs to user
    business = db.query(Business).filter(
        Business.id == content_data.business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Create content
    new_content = Content(
        business_id=content_data.business_id,
        platform=Platform[content_data.platform.upper()],
        content_type=ContentType[content_data.content_type.upper()],
        tone=ContentTone[content_data.tone.upper()],
        text=content_data.text,
        hashtags=content_data.hashtags,
        scheduled_for=content_data.scheduled_for,
        status=ContentStatus.SCHEDULED if content_data.scheduled_for else ContentStatus.DRAFT,
        ai_generated=True,
        ai_model="anthropic/claude-3.5-sonnet"
    )
    
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    
    return new_content


@router.get("/", response_model=List[ContentResponse])
async def list_content(
    business_id: Optional[int] = None,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    List all content for the current user
    Filter by business_id, platform, or status
    """
    # Base query - join with Business to filter by user
    query = db.query(Content).join(Business).filter(Business.user_id == user_id)
    
    # Apply filters
    if business_id:
        query = query.filter(Content.business_id == business_id)
    
    if platform:
        query = query.filter(Content.platform == Platform[platform.upper()])
    
    if status:
        query = query.filter(Content.status == ContentStatus[status.upper()])
    
    # Order by scheduled date or created date
    content = query.order_by(
        Content.scheduled_for.desc().nullslast(),
        Content.created_at.desc()
    ).all()
    
    return content


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get a specific content item by ID
    """
    content = db.query(Content).join(Business).filter(
        Content.id == content_id,
        Business.user_id == user_id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    return content


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int,
    content_data: ContentUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Update a content item
    """
    content = db.query(Content).join(Business).filter(
        Content.id == content_id,
        Business.user_id == user_id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Update fields if provided
    update_data = content_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status" and value:
            value = ContentStatus[value.upper()]
        setattr(content, field, value)
    
    db.commit()
    db.refresh(content)
    
    return content


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a content item
    """
    content = db.query(Content).join(Business).filter(
        Content.id == content_id,
        Business.user_id == user_id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    db.delete(content)
    db.commit()
    
    return None


@router.get("/calendar/{business_id}", response_model=List[ContentResponse])
async def get_content_calendar(
    business_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get content calendar for a specific business
    Filter by date range if provided
    """
    # Verify business exists and belongs to user
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Build query
    query = db.query(Content).filter(Content.business_id == business_id)
    
    if start_date:
        query = query.filter(Content.scheduled_for >= start_date)
    
    if end_date:
        query = query.filter(Content.scheduled_for <= end_date)
    
    # Order by scheduled date
    content = query.order_by(Content.scheduled_for.asc()).all()
    
    return content
