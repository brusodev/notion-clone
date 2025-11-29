from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class PageBase(BaseModel):
    title: str = Field(default="Untitled", max_length=500)
    icon: Optional[str] = Field(None, max_length=100)
    cover_image: Optional[str] = Field(None, max_length=500)


class PageCreate(BaseModel):
    workspace_id: UUID
    parent_id: Optional[UUID] = None
    title: str = Field(default="Untitled", max_length=500)
    icon: Optional[str] = Field(None, max_length=100)
    cover_image: Optional[str] = Field(None, max_length=500)
    order: int = Field(default=0)


class PageUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=100)
    cover_image: Optional[str] = Field(None, max_length=500)
    is_public: Optional[bool] = None
    public_slug: Optional[str] = Field(None, max_length=100)


class PageMove(BaseModel):
    new_parent_id: Optional[UUID] = None
    new_order: int


class PageResponse(PageBase):
    id: UUID
    workspace_id: UUID
    parent_id: Optional[UUID] = None
    is_archived: bool
    is_public: bool
    public_slug: Optional[str] = None
    order: int
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PageWithBlocks(PageResponse):
    blocks: List["BlockResponse"] = []


class PageTree(PageResponse):
    children: List["PageTree"] = []


# Forward reference resolution
from app.schemas.block import BlockResponse
PageWithBlocks.model_rebuild()
