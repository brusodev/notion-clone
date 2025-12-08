import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import GUID


class Block(Base):
    __tablename__ = "blocks"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    page_id = Column(GUID, ForeignKey("pages.id", ondelete="CASCADE"), index=True, nullable=False)
    parent_block_id = Column(GUID, ForeignKey("blocks.id"), nullable=True, index=True)
    type = Column(String(50), nullable=False)  # 'paragraph', 'heading1', 'image', 'code', etc.
    content = Column(JSON, nullable=False)  # Flexible content structure (works in SQLite and PostgreSQL)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    page = relationship("Page", back_populates="blocks")
    parent_block = relationship("Block", remote_side=[id], back_populates="child_blocks")
    child_blocks = relationship("Block", back_populates="parent_block", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="block", cascade="all, delete-orphan")
