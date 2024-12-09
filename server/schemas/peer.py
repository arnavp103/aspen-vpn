"""Pydantic models for API validation"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PeerBase(BaseModel):
    """Base peer schema"""

    name: str = Field(..., min_length=1, max_length=64)
    public_key: str = Field(..., min_length=32, max_length=64)
    # regex pattern for IP address with CIDR notation
    assigned_ip: str = Field(
        ..., pattern=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$"
    )
    description: Optional[str] = None


class PeerCreate(PeerBase):
    """Schema for creating a new peer"""

    pass


class PeerUpdate(BaseModel):
    """Schema for updating a peer"""

    description: Optional[str] = None
    is_enabled: Optional[bool] = None


class PeerInDB(PeerBase):
    """Schema for peer information from database"""

    id: int
    api_key: str
    is_enabled: bool
    is_admin: bool
    last_seen: Optional[datetime] = None
    created_at: datetime
    last_modified: datetime

    class Config:
        # Allow ORM models to be passed to Pydantic models
        from_attributes = True
