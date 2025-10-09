"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    clerk_id: str


class UserResponse(UserBase):
    clerk_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BusinessBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_audience: Optional[str] = None
    marketing_goals: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_audience: Optional[str] = None
    marketing_goals: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None


class BusinessResponse(BusinessBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Strategy Schemas
class StrategyGenerateRequest(BaseModel):
    business_id: int
    additional_context: Optional[str] = None


class StrategyBase(BaseModel):
    title: str
    description: Optional[str] = None
    strategy_data: Dict[str, Any]
    status: Optional[str] = "draft"


class StrategyCreate(StrategyBase):
    business_id: int


class StrategyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    strategy_data: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class StrategyResponse(StrategyBase):
    id: int
    business_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
