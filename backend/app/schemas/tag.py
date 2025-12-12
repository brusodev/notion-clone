"""
Pydantic schemas for Tag and PageTag models
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from uuid import UUID
from typing import Optional
import re


class TagCreate(BaseModel):
    """Schema for creating a new tag"""
    name: str = Field(..., min_length=1, max_length=50, description="Tag name (1-50 characters)")
    color: Optional[str] = Field(None, description="Hex color code (e.g., #FF5733)")

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate hex color code format"""
        if v is None:
            return v
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex code (e.g., #FF5733)')
        return v.upper()  # Normalize to uppercase


class TagUpdate(BaseModel):
    """Schema for updating a tag"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="New tag name")
    color: Optional[str] = Field(None, description="New hex color code")

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate hex color code format"""
        if v is None:
            return v
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex code (e.g., #FF5733)')
        return v.upper()


class TagResponse(BaseModel):
    """Response schema for a tag"""
    id: UUID
    name: str
    color: Optional[str] = None
    workspace_id: UUID
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TagWithPageCount(BaseModel):
    """Tag response with count of pages using this tag"""
    id: UUID
    name: str
    color: Optional[str] = None
    workspace_id: UUID
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    page_count: int = Field(0, description="Number of pages with this tag")

    model_config = ConfigDict(from_attributes=True)


class PageTagResponse(BaseModel):
    """Response schema for a page-tag relationship"""
    id: UUID
    page_id: UUID
    tag_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
