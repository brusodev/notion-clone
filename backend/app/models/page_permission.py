"""
Page Permission model for controlling access to pages
"""

import uuid
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import GUID


class PermissionLevel(str, enum.Enum):
    """Permission levels for page access"""
    VIEW = "view"           # Can only view the page
    COMMENT = "comment"     # Can view and comment
    EDIT = "edit"          # Can edit the page


class PagePermission(Base):
    """
    Model for storing page-level permissions.
    Allows granular access control for individual pages.
    """
    __tablename__ = "page_permissions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)

    # The page being shared
    page_id = Column(GUID, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False, index=True)

    # The user receiving access
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Permission level
    permission_level = Column(
        SQLEnum(PermissionLevel),
        nullable=False,
        default=PermissionLevel.VIEW
    )

    # Who granted this permission
    granted_by = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    page = relationship("Page", backref="permissions", foreign_keys=[page_id])
    user = relationship("User", backref="page_permissions", foreign_keys=[user_id])
    granter = relationship("User", foreign_keys=[granted_by])

    # Constraints
    __table_args__ = (
        # Each user can only have one permission per page
        UniqueConstraint('page_id', 'user_id', name='uq_page_user_permission'),
    )

    def __repr__(self):
        return f"<PagePermission(page={self.page_id}, user={self.user_id}, level={self.permission_level})>"

    def can_view(self) -> bool:
        """Check if this permission allows viewing"""
        return self.permission_level in [PermissionLevel.VIEW, PermissionLevel.COMMENT, PermissionLevel.EDIT]

    def can_comment(self) -> bool:
        """Check if this permission allows commenting"""
        return self.permission_level in [PermissionLevel.COMMENT, PermissionLevel.EDIT]

    def can_edit(self) -> bool:
        """Check if this permission allows editing"""
        return self.permission_level == PermissionLevel.EDIT
