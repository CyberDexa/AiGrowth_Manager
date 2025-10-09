"""
Strategies API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.core.auth import get_current_user_id
from app.models.strategy import Strategy
from app.models.business import Business
from app.schemas import (
    StrategyGenerateRequest,
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse
)
from app.services.ai_service import ai_service

router = APIRouter()


@router.post("/generate", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def generate_strategy(
    request: StrategyGenerateRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate a new marketing strategy using AI
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
    
    # Check if business has required information
    if not business.name or not business.description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business must have name and description to generate strategy"
        )
    
    # Generate strategy using AI
    ai_result = await ai_service.generate_strategy(
        business_name=business.name,
        business_description=business.description or "",
        target_audience=business.target_audience or "General audience",
        marketing_goals=business.marketing_goals or "Increase brand awareness and sales",
        additional_context=request.additional_context
    )
    
    if not ai_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate strategy: {ai_result.get('error')}"
        )
    
    # Create strategy title
    strategy_title = f"{business.name} Marketing Strategy"
    
    # Save strategy to database
    db_strategy = Strategy(
        business_id=business.id,
        title=strategy_title,
        description=ai_result["strategy"].get("executive_summary", "AI-generated marketing strategy"),
        strategy_data=ai_result["strategy"],
        status="draft"
    )
    
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    
    return db_strategy


@router.get("/", response_model=List[StrategyResponse])
async def list_strategies(
    business_id: int = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    List all strategies for the current user
    Optionally filter by business_id
    """
    query = db.query(Strategy).join(Business).filter(Business.user_id == user_id)
    
    if business_id:
        query = query.filter(Strategy.business_id == business_id)
    
    strategies = query.order_by(Strategy.created_at.desc()).all()
    return strategies


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get a specific strategy by ID
    """
    strategy = db.query(Strategy).join(Business).filter(
        Strategy.id == strategy_id,
        Business.user_id == user_id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    return strategy


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: int,
    strategy_update: StrategyUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Update a strategy
    """
    strategy = db.query(Strategy).join(Business).filter(
        Strategy.id == strategy_id,
        Business.user_id == user_id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    # Update fields
    update_data = strategy_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(strategy, field, value)
    
    db.commit()
    db.refresh(strategy)
    
    return strategy


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a strategy
    """
    strategy = db.query(Strategy).join(Business).filter(
        Strategy.id == strategy_id,
        Business.user_id == user_id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    db.delete(strategy)
    db.commit()
    
    return None
