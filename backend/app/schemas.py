"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# User Schemas
class UserCreate(BaseModel):
    clerk_id: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserResponse(BaseModel):
    clerk_id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Business Schemas
class BusinessCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_audience: Optional[str] = None
    marketing_goals: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_audience: Optional[str] = None
    marketing_goals: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None


class BusinessResponse(BaseModel):
    id: int
    user_id: str
    name: str
    description: Optional[str]
    target_audience: Optional[str]
    marketing_goals: Optional[str]
    industry: Optional[str]
    company_size: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
