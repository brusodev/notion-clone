import uuid
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import GUID


class Comment(Base):
    __tablename__ = "comments"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    page_id = Column(GUID, ForeignKey("pages.id", ondelete="CASCADE"), index=True, nullable=True)
    block_id = Column(GUID, ForeignKey("blocks.id", ondelete="CASCADE"), index=True, nullable=True)
    parent_comment_id = Column(GUID, ForeignKey("comments.id", ondelete="CASCADE"), index=True, nullable=True)
    thread_depth = Column(Integer, default=0, nullable=False, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    edited_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    page = relationship("Page", back_populates="comments")
    block = relationship("Block", back_populates="comments")
    author = relationship("User", foreign_keys=[author_id], back_populates="comments_authored")
    deleted_by_user = relationship("User", foreign_keys=[deleted_by], back_populates="comments_deleted")
    parent_comment = relationship("Comment", remote_side=[id], back_populates="replies")
    replies = relationship("Comment", back_populates="parent_comment", cascade="all, delete-orphan")
    reactions = relationship("CommentReaction", back_populates="comment", cascade="all, delete-orphan")
    mentions = relationship("CommentMention", back_populates="comment", cascade="all, delete-orphan")
    attachments = relationship("CommentAttachment", back_populates="comment", cascade="all, delete-orphan", order_by="CommentAttachment.order_index")

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "(page_id IS NOT NULL AND block_id IS NULL) OR (page_id IS NULL AND block_id IS NOT NULL)",
            name="check_comment_target"
        ),
        CheckConstraint(
            "thread_depth >= 0 AND thread_depth <= 5",
            name="check_thread_depth"
        ),
    )
