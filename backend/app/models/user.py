import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import GUID


class User(Base):
    __tablename__ = "users"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    workspaces_owned = relationship("Workspace", back_populates="owner", cascade="all, delete-orphan")
    workspace_memberships = relationship("WorkspaceMember", back_populates="user", cascade="all, delete-orphan")
    pages_created = relationship("Page", back_populates="creator")
    comments_authored = relationship("Comment", foreign_keys="Comment.author_id", back_populates="author")
    comments_deleted = relationship("Comment", foreign_keys="Comment.deleted_by", back_populates="deleted_by_user")
    comment_reactions = relationship("CommentReaction", back_populates="user")
    comment_mentions_received = relationship("CommentMention", back_populates="mentioned_user")
    comment_attachments_uploaded = relationship("CommentAttachment", back_populates="uploader")
