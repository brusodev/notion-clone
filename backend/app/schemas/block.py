from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class BlockBase(BaseModel):
    type: str = Field(..., max_length=50)
    content: Dict[str, Any]


class BlockCreate(BaseModel):
    page_id: UUID
    parent_block_id: Optional[UUID] = None
    type: str = Field(..., max_length=50)
    content: Dict[str, Any]
    order: int


class BlockUpdate(BaseModel):
    type: Optional[str] = Field(None, max_length=50)
    content: Optional[Dict[str, Any]] = None


class BlockMove(BaseModel):
    new_order: int
    new_parent_block_id: Optional[UUID] = None


class BlockResponse(BlockBase):
    id: UUID
    page_id: UUID
    parent_block_id: Optional[UUID] = None
    order: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
