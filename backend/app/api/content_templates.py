"""
Content Templates API
Allows users to create, manage, and use reusable content templates
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime

from app.db.database import get_db
from app.core.auth import get_current_user
from app.models.content_template import ContentTemplate
from app.models.business import Business

router = APIRouter()


# Pydantic schemas
class TemplateBase(BaseModel):
    name: str = Field(..., max_length=255, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    category: Optional[str] = Field(None, max_length=100, description="Template category (e.g., 'Product Launch', 'Weekly Tips')")
    platform: Optional[str] = Field(None, max_length=50, description="Target platform (linkedin, twitter, facebook, instagram, or null for all)")
    template_structure: str = Field(..., description="Template content with placeholders like {{product_name}}, {{benefit}}")
    placeholders: Optional[dict] = Field(None, description="Dictionary of placeholder names and descriptions")
    is_public: bool = Field(False, description="Whether template is shared publicly")


class TemplateCreate(TemplateBase):
    business_id: int


class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    platform: Optional[str] = Field(None, max_length=50)
    template_structure: Optional[str] = None
    placeholders: Optional[dict] = None
    is_public: Optional[bool] = None


class TemplateResponse(TemplateBase):
    id: int
    business_id: int
    use_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    templates: List[TemplateResponse]
    total: int


class UseTemplateRequest(BaseModel):
    placeholder_values: dict = Field(..., description="Dictionary mapping placeholder names to values")


class UseTemplateResponse(BaseModel):
    content: str
    hashtags: Optional[str] = None


# Helper function to verify business ownership
def verify_business_ownership(business_id: int, current_user: dict, db: Session) -> Business:
    """Verify that the current user owns the business"""
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user["sub"]
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found or access denied"
        )
    
    return business


# Endpoints

@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new content template"""
    # Verify business ownership
    verify_business_ownership(template_data.business_id, current_user, db)
    
    # Create template
    template = ContentTemplate(
        business_id=template_data.business_id,
        name=template_data.name,
        description=template_data.description,
        category=template_data.category,
        platform=template_data.platform,
        template_structure=template_data.template_structure,
        placeholders=template_data.placeholders,
        is_public=template_data.is_public,
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return template


@router.get("/", response_model=TemplateListResponse)
async def list_templates(
    business_id: Optional[int] = None,
    category: Optional[str] = None,
    platform: Optional[str] = None,
    include_public: bool = True,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List content templates for a business"""
    query = db.query(ContentTemplate)
    
    # Filter by business or show public templates
    if business_id:
        verify_business_ownership(business_id, current_user, db)
        if include_public:
            query = query.filter(
                (ContentTemplate.business_id == business_id) |
                (ContentTemplate.is_public == True)
            )
        else:
            query = query.filter(ContentTemplate.business_id == business_id)
    elif include_public:
        query = query.filter(ContentTemplate.is_public == True)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide business_id or include_public=true"
        )
    
    # Filter by category
    if category:
        query = query.filter(ContentTemplate.category == category)
    
    # Filter by platform
    if platform:
        query = query.filter(
            (ContentTemplate.platform == platform) |
            (ContentTemplate.platform == None)
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination and order
    templates = query.order_by(ContentTemplate.use_count.desc(), ContentTemplate.created_at.desc()).offset(skip).limit(limit).all()
    
    return TemplateListResponse(templates=templates, total=total)


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific template by ID"""
    template = db.query(ContentTemplate).filter(ContentTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Check if user has access (owns the business or template is public)
    if not template.is_public:
        verify_business_ownership(template.business_id, current_user, db)
    
    return template


@router.patch("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a content template"""
    template = db.query(ContentTemplate).filter(ContentTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Verify ownership
    verify_business_ownership(template.business_id, current_user, db)
    
    # Update fields
    update_data = template_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a content template"""
    template = db.query(ContentTemplate).filter(ContentTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Verify ownership
    verify_business_ownership(template.business_id, current_user, db)
    
    db.delete(template)
    db.commit()
    
    return None


@router.post("/{template_id}/use", response_model=UseTemplateResponse)
async def use_template(
    template_id: int,
    use_data: UseTemplateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Use a template by filling in placeholder values"""
    template = db.query(ContentTemplate).filter(ContentTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Check if user has access
    if not template.is_public:
        verify_business_ownership(template.business_id, current_user, db)
    
    # Replace placeholders in template
    content = template.template_structure
    for placeholder, value in use_data.placeholder_values.items():
        content = content.replace(f"{{{{{placeholder}}}}}", str(value))
    
    # Extract hashtags if present
    hashtags = None
    if "\n#" in content:
        parts = content.split("\n#", 1)
        content = parts[0].strip()
        hashtags = "#" + parts[1].strip()
    
    # Increment use count
    template.use_count += 1
    db.commit()
    
    return UseTemplateResponse(content=content, hashtags=hashtags)


@router.get("/categories/list", response_model=List[str])
async def list_categories(
    business_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of all unique template categories"""
    query = db.query(ContentTemplate.category).distinct()
    
    if business_id:
        verify_business_ownership(business_id, current_user, db)
        query = query.filter(
            (ContentTemplate.business_id == business_id) |
            (ContentTemplate.is_public == True)
        )
    else:
        query = query.filter(ContentTemplate.is_public == True)
    
    categories = [cat[0] for cat in query.all() if cat[0] is not None]
    return categories
