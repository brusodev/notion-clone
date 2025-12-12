"""
CRUD operations for File model
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.file import File, FileType
from app.schemas.file import FileCreate


def create_file(db: Session, file_data: FileCreate, uploaded_by: UUID) -> File:
    """
    Create a new file record

    Args:
        db: Database session
        file_data: File creation data
        uploaded_by: ID of user uploading the file

    Returns:
        Created File instance
    """
    db_file = File(
        filename=file_data.filename,
        file_type=file_data.file_type,
        mime_type=file_data.mime_type,
        size_bytes=file_data.size_bytes,
        storage_provider=file_data.storage_provider,
        storage_url=file_data.storage_url,
        storage_id=file_data.storage_id,
        thumbnail_url=file_data.thumbnail_url,
        uploaded_by=uploaded_by,
        workspace_id=file_data.workspace_id,
        page_id=file_data.page_id,
        block_id=file_data.block_id,
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def get_file_by_id(db: Session, file_id: UUID) -> Optional[File]:
    """
    Get file by ID

    Args:
        db: Database session
        file_id: File ID

    Returns:
        File instance or None
    """
    return db.query(File).filter(File.id == file_id).first()


def get_files_by_workspace(
    db: Session,
    workspace_id: UUID,
    file_type: Optional[FileType] = None,
    skip: int = 0,
    limit: int = 100
) -> List[File]:
    """
    Get files in a workspace, optionally filtered by type

    Args:
        db: Database session
        workspace_id: Workspace ID
        file_type: Optional file type filter
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of File instances
    """
    query = db.query(File).filter(File.workspace_id == workspace_id)

    if file_type:
        query = query.filter(File.file_type == file_type)

    return query.order_by(File.created_at.desc()).offset(skip).limit(limit).all()


def get_files_by_page(
    db: Session,
    page_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> List[File]:
    """
    Get files attached to a specific page

    Args:
        db: Database session
        page_id: Page ID
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of File instances
    """
    return (
        db.query(File)
        .filter(File.page_id == page_id)
        .order_by(File.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_files_by_block(
    db: Session,
    block_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> List[File]:
    """
    Get files attached to a specific block

    Args:
        db: Database session
        block_id: Block ID
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of File instances
    """
    return (
        db.query(File)
        .filter(File.block_id == block_id)
        .order_by(File.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_files_by_user(
    db: Session,
    user_id: UUID,
    workspace_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100
) -> List[File]:
    """
    Get files uploaded by a specific user

    Args:
        db: Database session
        user_id: User ID
        workspace_id: Optional workspace filter
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of File instances
    """
    query = db.query(File).filter(File.uploaded_by == user_id)

    if workspace_id:
        query = query.filter(File.workspace_id == workspace_id)

    return query.order_by(File.created_at.desc()).offset(skip).limit(limit).all()


def delete_file(db: Session, file_id: UUID) -> bool:
    """
    Delete a file record

    Args:
        db: Database session
        file_id: File ID

    Returns:
        True if file was deleted, False if not found
    """
    db_file = db.query(File).filter(File.id == file_id).first()
    if db_file:
        db.delete(db_file)
        db.commit()
        return True
    return False


def get_workspace_storage_usage(db: Session, workspace_id: UUID) -> int:
    """
    Get total storage usage for a workspace in bytes

    Args:
        db: Database session
        workspace_id: Workspace ID

    Returns:
        Total size in bytes
    """
    from sqlalchemy import func

    result = (
        db.query(func.sum(File.size_bytes))
        .filter(File.workspace_id == workspace_id)
        .scalar()
    )
    return result or 0


def get_workspace_file_count(
    db: Session,
    workspace_id: UUID,
    file_type: Optional[FileType] = None
) -> int:
    """
    Get count of files in a workspace

    Args:
        db: Database session
        workspace_id: Workspace ID
        file_type: Optional file type filter

    Returns:
        Number of files
    """
    query = db.query(File).filter(File.workspace_id == workspace_id)

    if file_type:
        query = query.filter(File.file_type == file_type)

    return query.count()
