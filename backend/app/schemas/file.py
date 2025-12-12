"""
Pydantic schemas for File operations
"""

from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.file import FileType


class FileBase(BaseModel):
    """Base schema for File"""
    filename: str = Field(..., min_length=1, max_length=255)
    file_type: FileType
    mime_type: Optional[str] = Field(None, max_length=100)
    size_bytes: int = Field(..., gt=0)
    storage_provider: str = Field(default="cloudinary", max_length=50)
    storage_url: str = Field(..., max_length=500)
    storage_id: Optional[str] = Field(None, max_length=255)
    thumbnail_url: Optional[str] = Field(None, max_length=500)


class FileCreate(FileBase):
    """Schema for creating a File"""
    workspace_id: UUID
    page_id: Optional[UUID] = None
    block_id: Optional[UUID] = None

    @field_validator('page_id', 'block_id')
    @classmethod
    def validate_optional_uuids(cls, v):
        """Validate optional UUID fields"""
        if v is not None and not isinstance(v, UUID):
            raise ValueError('Invalid UUID')
        return v


class FileUpdate(BaseModel):
    """Schema for updating a File (limited fields)"""
    filename: Optional[str] = Field(None, min_length=1, max_length=255)
    page_id: Optional[UUID] = None
    block_id: Optional[UUID] = None


class FileInDB(FileBase):
    """Schema for File in database"""
    id: UUID
    uploaded_by: Optional[UUID]
    workspace_id: UUID
    page_id: Optional[UUID]
    block_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FileResponse(FileInDB):
    """Schema for File response with computed fields"""
    size_kb: float
    size_mb: float

    @staticmethod
    def from_orm_with_sizes(file) -> "FileResponse":
        """Create FileResponse from ORM model with computed sizes"""
        return FileResponse(
            id=file.id,
            filename=file.filename,
            file_type=file.file_type,
            mime_type=file.mime_type,
            size_bytes=file.size_bytes,
            storage_provider=file.storage_provider,
            storage_url=file.storage_url,
            storage_id=file.storage_id,
            thumbnail_url=file.thumbnail_url,
            uploaded_by=file.uploaded_by,
            workspace_id=file.workspace_id,
            page_id=file.page_id,
            block_id=file.block_id,
            created_at=file.created_at,
            updated_at=file.updated_at,
            size_kb=file.size_kb,
            size_mb=file.size_mb,
        )


class FileUploadRequest(BaseModel):
    """Schema for file upload request metadata"""
    workspace_id: UUID
    page_id: Optional[UUID] = None
    block_id: Optional[UUID] = None
    folder: Optional[str] = Field(default="notion-clone", max_length=100)


class FileListResponse(BaseModel):
    """Schema for paginated file list response"""
    files: list[FileResponse]
    total: int
    skip: int
    limit: int


class WorkspaceStorageStats(BaseModel):
    """Schema for workspace storage statistics"""
    workspace_id: UUID
    total_files: int
    total_size_bytes: int
    total_size_mb: float
    files_by_type: dict[str, int]

    class Config:
        from_attributes = True
