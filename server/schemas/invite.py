"""Pydantic models for invite validation"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class InviteBase(BaseModel):
    """Base invite schema"""

    code: str = Field(..., min_length=1, max_length=64)
    expires_at: Optional[datetime] = None
    description: Optional[str] = None
    used_by: Optional[int] = None

class InviteCreate(InviteBase):
    """Schema for creating a new invite"""

    pass

class InviteUpdate(BaseModel):
    """Schema for updating an invite"""

    description: Optional[str] = None
    expires_at: Optional[datetime] = None
    used_by: Optional[int] = None

class InviteInDB(InviteBase):
    """Schema for invite information from database"""

    id: int
    created_at: datetime
    last_modified: datetime

    class Config:
        # Allow ORM models to be passed to Pydantic models
        from_attributes = True