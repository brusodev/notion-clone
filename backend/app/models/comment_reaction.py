import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import GUID


class CommentReaction(Base):
    __tablename__ = "comment_reactions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    comment_id = Column(GUID, ForeignKey("comments.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    reaction_type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    comment = relationship("Comment", back_populates="reactions")
    user = relationship("User", back_populates="comment_reactions")

    # Table constraints
    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", "reaction_type", name="uq_comment_user_reaction"),
    )
