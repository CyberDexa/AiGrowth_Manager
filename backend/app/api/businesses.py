"""
API endpoints for business management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.business import Business
from app.models.user import User
from app.schemas import BusinessCreate, BusinessUpdate, BusinessResponse
from app.core.auth import get_current_user_id, get_current_user

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.post("/", response_model=BusinessResponse, status_code=201)
async def create_business(
    business_data: BusinessCreate,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new business (from onboarding form)
    Auto-creates user if they don't exist
    """
    user_id = user_data.get("sub")
    
    # Check if user exists, if not create them
    user = db.query(User).filter(User.clerk_id == user_id).first()
    if not user:
        # Create user from Clerk token data
        user = User(
            clerk_id=user_id,
            email=user_data.get("email", ""),
            first_name=user_data.get("given_name"),
            last_name=user_data.get("family_name")
        )
        db.add(user)
        db.flush()  # Flush to ensure user is in DB before creating business
    
    # Create new business
    new_business = Business(
        user_id=user_id,
        name=business_data.name,
        description=business_data.description,
        target_audience=business_data.target_audience,
        marketing_goals=business_data.marketing_goals,
        industry=business_data.industry,
        company_size=business_data.company_size,
    )
    
    db.add(new_business)
    db.commit()
    db.refresh(new_business)
    
    return new_business


@router.get("/", response_model=List[BusinessResponse])
async def get_user_businesses(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all businesses for the current user
    """
    businesses = db.query(Business).filter(Business.user_id == user_id).all()
    return businesses


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(
    business_id: int,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific business by ID
    """
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    return business


@router.put("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: int,
    business_data: BusinessUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update a business
    """
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Update fields if provided
    update_data = business_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(business, field, value)
    
    db.commit()
    db.refresh(business)
    
    return business


@router.delete("/{business_id}", status_code=204)
async def delete_business(
    business_id: int,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a business
    """
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == user_id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    db.delete(business)
    db.commit()
    
    return None
