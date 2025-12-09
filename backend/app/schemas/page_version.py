from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class PageVersionBase(BaseModel):
    title: str
    content_snapshot: List[Dict[str, Any]]


class PageVersionCreate(BaseModel):
    change_summary: Optional[str] = None


class PageVersionResponse(PageVersionBase):
    id: UUID
    page_id: UUID
    version_number: int
    icon: Optional[str] = None
    cover_image: Optional[str] = None
    created_at: datetime
    created_by: Optional[UUID] = None
    change_summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PageVersionListItem(BaseModel):
    """Simplified version for listing"""
    id: UUID
    version_number: int
    title: str
    created_at: datetime
    created_by: Optional[UUID] = None
    change_summary: Optional[str] = None
    blocks_count: int  # Number of blocks in snapshot

    model_config = ConfigDict(from_attributes=True)
