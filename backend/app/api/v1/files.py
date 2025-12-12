"""
API endpoints for file upload and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.file import FileType
from app.schemas.file import (
    FileResponse,
    FileListResponse,
    FileCreate,
    WorkspaceStorageStats
)
from app.crud import file as crud_file
from app.crud import workspace as crud_workspace
from app.services.upload import upload_service

router = APIRouter()


def verify_workspace_access(
    workspace_id: UUID,
    user: User,
    db: Session
) -> None:
    """
    Verify user has access to workspace

    Raises:
        HTTPException: If user doesn't have access
    """
    if not crud_workspace.is_member(db, workspace_id=workspace_id, user_id=user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this workspace"
        )


@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    workspace_id: UUID = Form(...),
    page_id: Optional[UUID] = Form(None),
    block_id: Optional[UUID] = Form(None),
    folder: Optional[str] = Form("notion-clone"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a file to Cloudinary and create database record

    - **file**: File to upload (multipart/form-data)
    - **workspace_id**: ID of the workspace
    - **page_id**: Optional ID of the page to attach to
    - **block_id**: Optional ID of the block to attach to
    - **folder**: Optional Cloudinary folder path
    """
    # Verify workspace access
    verify_workspace_access(workspace_id, current_user, db)

    # Upload file to Cloudinary
    try:
        upload_result = await upload_service.upload_file(
            file=file,
            folder=folder,
            workspace_id=str(workspace_id)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

    # Create database record
    file_create = FileCreate(
        filename=upload_result["filename"],
        file_type=upload_result["file_type"],
        mime_type=upload_result["mime_type"],
        size_bytes=upload_result["size_bytes"],
        storage_provider="cloudinary",
        storage_url=upload_result["storage_url"],
        storage_id=upload_result["storage_id"],
        thumbnail_url=upload_result.get("thumbnail_url"),
        workspace_id=workspace_id,
        page_id=page_id,
        block_id=block_id
    )

    db_file = crud_file.create_file(db, file_create, current_user.id)
    return FileResponse.from_orm_with_sizes(db_file)


@router.get("/{file_id}", response_model=FileResponse)
def get_file(
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get file by ID

    - **file_id**: File ID
    """
    db_file = crud_file.get_file_by_id(db, file_id)
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Verify workspace access
    verify_workspace_access(db_file.workspace_id, current_user, db)

    return FileResponse.from_orm_with_sizes(db_file)


@router.get("/workspace/{workspace_id}", response_model=FileListResponse)
def get_workspace_files(
    workspace_id: UUID,
    file_type: Optional[FileType] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get files in a workspace

    - **workspace_id**: Workspace ID
    - **file_type**: Optional file type filter (image, video, document, audio, other)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 100)
    """
    # Verify workspace access
    verify_workspace_access(workspace_id, current_user, db)

    # Limit max to 100
    limit = min(limit, 100)

    # Get files
    files = crud_file.get_files_by_workspace(
        db, workspace_id, file_type, skip, limit
    )

    # Get total count
    total = crud_file.get_workspace_file_count(db, workspace_id, file_type)

    return FileListResponse(
        files=[FileResponse.from_orm_with_sizes(f) for f in files],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/page/{page_id}", response_model=FileListResponse)
def get_page_files(
    page_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get files attached to a page

    - **page_id**: Page ID
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 100)
    """
    # Get files
    files = crud_file.get_files_by_page(db, page_id, skip, min(limit, 100))

    # Verify access to at least one file
    if files:
        verify_workspace_access(files[0].workspace_id, current_user, db)

    # Get total count
    total = len(files)  # Simple count for now

    return FileListResponse(
        files=[FileResponse.from_orm_with_sizes(f) for f in files],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/block/{block_id}", response_model=FileListResponse)
def get_block_files(
    block_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get files attached to a block

    - **block_id**: Block ID
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 100)
    """
    # Get files
    files = crud_file.get_files_by_block(db, block_id, skip, min(limit, 100))

    # Verify access to at least one file
    if files:
        verify_workspace_access(files[0].workspace_id, current_user, db)

    # Get total count
    total = len(files)  # Simple count for now

    return FileListResponse(
        files=[FileResponse.from_orm_with_sizes(f) for f in files],
        total=total,
        skip=skip,
        limit=limit
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a file (both from Cloudinary and database)

    - **file_id**: File ID
    """
    # Get file
    db_file = crud_file.get_file_by_id(db, file_id)
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Verify workspace access
    verify_workspace_access(db_file.workspace_id, current_user, db)

    # Delete from Cloudinary
    if db_file.storage_id:
        try:
            await upload_service.delete_file(db_file.storage_id)
        except Exception as e:
            # Log error but continue with database deletion
            print(f"Failed to delete file from Cloudinary: {e}")

    # Delete from database
    crud_file.delete_file(db, file_id)


@router.get("/workspace/{workspace_id}/stats", response_model=WorkspaceStorageStats)
def get_workspace_storage_stats(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get storage statistics for a workspace

    - **workspace_id**: Workspace ID
    """
    # Verify workspace access
    verify_workspace_access(workspace_id, current_user, db)

    # Get total storage usage
    total_size_bytes = crud_file.get_workspace_storage_usage(db, workspace_id)
    total_size_mb = round(total_size_bytes / (1024 * 1024), 2)

    # Get total file count
    total_files = crud_file.get_workspace_file_count(db, workspace_id)

    # Get file counts by type
    files_by_type = {}
    for file_type in FileType:
        count = crud_file.get_workspace_file_count(db, workspace_id, file_type)
        if count > 0:
            files_by_type[file_type.value] = count

    return WorkspaceStorageStats(
        workspace_id=workspace_id,
        total_files=total_files,
        total_size_bytes=total_size_bytes,
        total_size_mb=total_size_mb,
        files_by_type=files_by_type
    )
