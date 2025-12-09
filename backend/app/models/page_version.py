import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import GUID


class PageVersion(Base):
    __tablename__ = "page_versions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    page_id = Column(GUID, ForeignKey("pages.id", ondelete="CASCADE"), index=True, nullable=False)
    version_number = Column(Integer, nullable=False)

    # Snapshot data
    title = Column(String(500), nullable=False)
    icon = Column(String(100), nullable=True)
    cover_image = Column(String(500), nullable=True)
    content_snapshot = Column(JSON, nullable=False)  # Snapshot of all blocks

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    change_summary = Column(Text, nullable=True)  # Optional description of changes

    # Relationships
    page = relationship("Page", back_populates="versions")
    creator = relationship("User")

    def __repr__(self):
        return f"<PageVersion(page_id={self.page_id}, version={self.version_number})>"
