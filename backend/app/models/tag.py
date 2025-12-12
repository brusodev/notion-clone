"""
Tag model for organizing pages with labels/categories.
Allows users to create custom tags within a workspace and apply them to pages.
"""

import uuid
from sqlalchemy import Column, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.core.database import Base
from app.core.types import GUID


class Tag(Base):
    """
    Tag model for categorizing pages within a workspace.
    Each tag has a name and optional color for visual distinction.
    """
    __tablename__ = "tags"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, index=True)
    color = Column(String(7), nullable=True)  # Hex color code like #FF5733
    workspace_id = Column(GUID, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    workspace = relationship("Workspace", backref="tags")
    creator = relationship("User", backref="created_tags")
    page_tags = relationship("PageTag", back_populates="tag", cascade="all, delete-orphan")

    # Constraints: Tag name must be unique within a workspace
    __table_args__ = (
        UniqueConstraint('workspace_id', 'name', name='uq_workspace_tag_name'),
        Index('ix_tags_workspace_id_name', 'workspace_id', 'name'),
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', workspace_id={self.workspace_id})>"


class PageTag(Base):
    """
    Junction table for many-to-many relationship between Pages and Tags.
    Tracks which tags are applied to which pages.
    """
    __tablename__ = "page_tags"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    page_id = Column(GUID, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id = Column(GUID, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    page = relationship("Page", backref="page_tags")
    tag = relationship("Tag", back_populates="page_tags")

    # Constraints: A tag can only be applied once to a page
    __table_args__ = (
        UniqueConstraint('page_id', 'tag_id', name='uq_page_tag'),
        Index('ix_page_tags_page_id_tag_id', 'page_id', 'tag_id'),
    )

    def __repr__(self):
        return f"<PageTag(page_id={self.page_id}, tag_id={self.tag_id})>"
