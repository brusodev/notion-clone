import uuid
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import GUID


class CommentMention(Base):
    __tablename__ = "comment_mentions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    comment_id = Column(GUID, ForeignKey("comments.id", ondelete="CASCADE"), index=True, nullable=False)
    mentioned_user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    comment = relationship("Comment", back_populates="mentions")
    mentioned_user = relationship("User", back_populates="comment_mentions_received")

    # Table constraints
    __table_args__ = (
        UniqueConstraint("comment_id", "mentioned_user_id", name="uq_comment_mention"),
    )
