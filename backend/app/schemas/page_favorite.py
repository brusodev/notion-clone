from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


class PageFavoriteResponse(BaseModel):
    """Response schema for a page favorite"""
    id: UUID
    user_id: UUID
    page_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PageFavoriteStatus(BaseModel):
    """Response schema for favorite status check"""
    is_favorited: bool
    favorited_at: datetime | None = None
