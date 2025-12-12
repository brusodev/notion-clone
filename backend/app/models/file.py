"""
File model for storing uploaded files metadata.
Actual files are stored in Cloudinary (or other cloud storage).
"""

import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.types import GUID
import enum


class FileType(str, enum.Enum):
    """Enum for file types"""
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"
    OTHER = "other"


class File(Base):
    """
    Model for storing file metadata.
    The actual file is stored in cloud storage (Cloudinary).
    """
    __tablename__ = "files"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)

    # File metadata
    filename = Column(String(255), nullable=False)  # Original filename
    file_type = Column(SQLEnum(FileType), nullable=False, default=FileType.OTHER)
    mime_type = Column(String(100), nullable=True)  # e.g., "image/png", "application/pdf"
    size_bytes = Column(Integer, nullable=False)  # File size in bytes

    # Cloud storage info
    storage_provider = Column(String(50), nullable=False, default="cloudinary")  # cloudinary, s3, etc.
    storage_url = Column(String(500), nullable=False)  # Full URL to access the file
    storage_id = Column(String(255), nullable=True)  # Provider-specific ID (e.g., Cloudinary public_id)

    # Optional: Thumbnail for images/videos
    thumbnail_url = Column(String(500), nullable=True)

    # Relationships
    uploaded_by = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    workspace_id = Column(GUID, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)

    # Optional: Link to specific block or page
    page_id = Column(GUID, ForeignKey("pages.id", ondelete="CASCADE"), nullable=True, index=True)
    block_id = Column(GUID, ForeignKey("blocks.id", ondelete="CASCADE"), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    uploader = relationship("User", backref="uploaded_files")
    workspace = relationship("Workspace", backref="files")
    page = relationship("Page", backref="attached_files")
    block = relationship("Block", backref="attached_files")

    # Indexes for common queries
    __table_args__ = (
        Index('ix_files_workspace_type', 'workspace_id', 'file_type'),
        Index('ix_files_page', 'page_id'),
        Index('ix_files_block', 'block_id'),
    )

    def __repr__(self):
        return f"<File(id={self.id}, filename='{self.filename}', type={self.file_type})>"

    @property
    def size_kb(self) -> float:
        """Get file size in kilobytes"""
        return round(self.size_bytes / 1024, 2)

    @property
    def size_mb(self) -> float:
        """Get file size in megabytes"""
        return round(self.size_bytes / (1024 * 1024), 2)
