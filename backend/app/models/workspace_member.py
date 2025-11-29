import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base
from app.core.types import GUID


class WorkspaceRole(str, enum.Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID, ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    role = Column(Enum(WorkspaceRole), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspace_memberships")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_user"),
    )
