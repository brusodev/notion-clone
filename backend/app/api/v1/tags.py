"""
API endpoints for Tag management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.crud import workspace as crud_workspace
from app.crud import page as crud_page
from app.crud import tag as crud_tag
from app.schemas.tag import (
    TagCreate,
    TagUpdate,
    TagResponse,
    TagWithPageCount,
    PageTagResponse
)
from app.schemas.page import PageResponse

router = APIRouter()


# Workspace-level tag endpoints

@router.post("/workspaces/{workspace_id}/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    workspace_id: UUID,
    tag_data: TagCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new tag in a workspace.
    User must be a member of the workspace.
    """
    # Check if user is a member of the workspace
    if not crud_workspace.is_member(db, workspace_id=workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )

    # Create the tag
    tag = crud_tag.create_tag(
        db=db,
        name=tag_data.name,
        workspace_id=workspace_id,
        created_by=current_user.id,
        color=tag_data.color
    )

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tag with name '{tag_data.name}' already exists in this workspace"
        )

    return tag


@router.get("/workspaces/{workspace_id}/tags", response_model=List[TagWithPageCount])
def list_workspace_tags(
    workspace_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all tags for a workspace with page counts.
    User must be a member of the workspace.
    """
    # Check if user is a member of the workspace
    if not crud_workspace.is_member(db, workspace_id=workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )

    # Get tags
    tags = crud_tag.get_workspace_tags(db=db, workspace_id=workspace_id, skip=skip, limit=limit)

    # Add page counts
    tags_with_counts = []
    for tag in tags:
        page_count = crud_tag.get_page_count_for_tag(db=db, tag_id=tag.id)
        tag_dict = {
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
            "workspace_id": tag.workspace_id,
            "created_by": tag.created_by,
            "created_at": tag.created_at,
            "updated_at": tag.updated_at,
            "page_count": page_count
        }
        tags_with_counts.append(TagWithPageCount(**tag_dict))

    return tags_with_counts


@router.get("/workspaces/{workspace_id}/tags/{tag_id}", response_model=TagResponse)
def get_tag(
    workspace_id: UUID,
    tag_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific tag by ID.
    User must be a member of the workspace.
    """
    # Check if user is a member of the workspace
    if not crud_workspace.is_member(db, workspace_id=workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )

    # Get tag
    tag = crud_tag.get_tag_by_id(db=db, tag_id=tag_id)
    if not tag or tag.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    return tag


@router.put("/workspaces/{workspace_id}/tags/{tag_id}", response_model=TagResponse)
def update_tag(
    workspace_id: UUID,
    tag_id: UUID,
    tag_data: TagUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a tag's name or color.
    User must be a member of the workspace.
    """
    # Check if user is a member of the workspace
    if not crud_workspace.is_member(db, workspace_id=workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )

    # Get tag
    tag = crud_tag.get_tag_by_id(db=db, tag_id=tag_id)
    if not tag or tag.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    # Update tag
    updated_tag = crud_tag.update_tag(
        db=db,
        tag_id=tag_id,
        name=tag_data.name,
        color=tag_data.color
    )

    if not updated_tag:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tag with this name already exists in the workspace"
        )

    return updated_tag


@router.delete("/workspaces/{workspace_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    workspace_id: UUID,
    tag_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a tag. This will also remove it from all pages.
    User must be a member of the workspace.
    """
    # Check if user is a member of the workspace
    if not crud_workspace.is_member(db, workspace_id=workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )

    # Get tag
    tag = crud_tag.get_tag_by_id(db=db, tag_id=tag_id)
    if not tag or tag.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    # Delete tag
    deleted = crud_tag.delete_tag(db=db, tag_id=tag_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )


@router.get("/workspaces/{workspace_id}/tags/{tag_id}/pages", response_model=List[PageResponse])
def get_pages_by_tag(
    workspace_id: UUID,
    tag_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all pages with a specific tag.
    User must be a member of the workspace.
    """
    # Check if user is a member of the workspace
    if not crud_workspace.is_member(db, workspace_id=workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )

    # Get tag
    tag = crud_tag.get_tag_by_id(db=db, tag_id=tag_id)
    if not tag or tag.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    # Get pages
    pages = crud_tag.get_pages_by_tag(
        db=db,
        tag_id=tag_id,
        workspace_id=workspace_id,
        skip=skip,
        limit=limit
    )

    return pages


# Page-level tag endpoints

@router.post("/pages/{page_id}/tags/{tag_id}", response_model=PageTagResponse, status_code=status.HTTP_201_CREATED)
def add_tag_to_page(
    page_id: UUID,
    tag_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a tag to a page.
    User must be a member of the page's workspace.
    """
    # Get page
    page = crud_page.get_by_id(db=db, page_id=page_id)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )

    # Check if user is a member of the workspace
    if not crud_workspace.is_member(db, workspace_id=page.workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )

    # Get tag and verify it belongs to the same workspace
    tag = crud_tag.get_tag_by_id(db=db, tag_id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    if tag.workspace_id != page.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag and page must be in the same workspace"
        )

    # Add tag to page
    page_tag = crud_tag.add_tag_to_page(db=db, page_id=page_id, tag_id=tag_id)
    if not page_tag:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tag is already applied to this page"
        )

    return page_tag


@router.delete("/pages/{page_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tag_from_page(
    page_id: UUID,
    tag_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove a tag from a page.
    User must be a member of the page's workspace.
    """
    # Get page
    page = crud_page.get_by_id(db=db, page_id=page_id)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )

    # Check if user is a member of the workspace
    if not crud_workspace.is_member(db, workspace_id=page.workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )

    # Remove tag from page
    removed = crud_tag.remove_tag_from_page(db=db, page_id=page_id, tag_id=tag_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not applied to this page"
        )


@router.get("/pages/{page_id}/tags", response_model=List[TagResponse])
def get_page_tags(
    page_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all tags for a specific page.
    User must be a member of the page's workspace.
    """
    # Get page
    page = crud_page.get_by_id(db=db, page_id=page_id)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )

    # Check if user is a member of the workspace
    if not crud_workspace.is_member(db, workspace_id=page.workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )

    # Get tags
    tags = crud_tag.get_page_tags(db=db, page_id=page_id)

    return tags
