import uuid
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import GUID


class Page(Base):
    __tablename__ = "pages"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID, ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False)
    parent_id = Column(GUID, ForeignKey("pages.id", ondelete="CASCADE"), index=True, nullable=True)
    title = Column(String(500), default="Untitled", nullable=False)
    icon = Column(String(100), nullable=True)  # emoji
    cover_image = Column(String(500), nullable=True)  # URL
    is_archived = Column(Boolean, default=False, index=True, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    public_slug = Column(String(100), unique=True, index=True, nullable=True)
    order = Column(Integer, default=0, nullable=False)
    created_by = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="pages")
    parent = relationship("Page", remote_side=[id], back_populates="children")
    children = relationship("Page", back_populates="parent", cascade="all, delete-orphan")
    creator = relationship("User", back_populates="pages_created")
    blocks = relationship("Block", back_populates="page", cascade="all, delete-orphan", order_by="Block.order")
    comments = relationship("Comment", back_populates="page", cascade="all, delete-orphan")
