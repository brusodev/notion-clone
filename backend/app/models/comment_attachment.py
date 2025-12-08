import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import GUID


class CommentAttachment(Base):
    __tablename__ = "comment_attachments"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    comment_id = Column(GUID, ForeignKey("comments.id", ondelete="CASCADE"), index=True, nullable=False)
    file_name = Column(String(500), nullable=False)
    file_url = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    mime_type = Column(String(100), nullable=True)
    uploaded_by = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    comment = relationship("Comment", back_populates="attachments")
    uploader = relationship("User", back_populates="comment_attachments_uploaded")
