import uuid
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import GUID


class PageFavorite(Base):
    """
    Model for user's favorite pages.
    Allows users to bookmark/favorite pages for quick access.
    """
    __tablename__ = "page_favorites"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    page_id = Column(GUID, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="favorites")
    page = relationship("Page", backref="favorited_by")

    # Ensure a user can only favorite a page once
    __table_args__ = (
        UniqueConstraint('user_id', 'page_id', name='uq_user_page_favorite'),
    )

    def __repr__(self):
        return f"<PageFavorite(user_id={self.user_id}, page_id={self.page_id})>"
