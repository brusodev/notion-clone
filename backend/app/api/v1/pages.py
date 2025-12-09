from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.api.deps import get_db, get_current_active_user
from app.crud import page as crud_page
from app.crud import workspace as crud_workspace
from app.schemas.page import PageCreate, PageUpdate, PageMove, PageResponse, PageWithBlocks, PageTree
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[PageResponse])
def list_pages(
    workspace_id: UUID = Query(..., description="Workspace ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all pages in a workspace"""
    # Check if user is a member of the workspace
    if not crud_workspace.is_member(db, workspace_id=workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )
    
    pages = crud_page.get_by_workspace(db, workspace_id=workspace_id)
    return pages


@router.post("/", response_model=PageResponse, status_code=status.HTTP_201_CREATED)
def create_page(
    page_in: PageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new page"""
    # Check if user is a member of the workspace
    if not crud_workspace.is_member(db, workspace_id=page_in.workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )
    
    # If parent_id is provided, verify it exists and belongs to same workspace
    if page_in.parent_id:
        parent_page = crud_page.get_by_id(db, page_id=page_in.parent_id)
        if not parent_page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent page not found"
            )
        if parent_page.workspace_id != page_in.workspace_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent page must be in the same workspace"
            )
    
    page = crud_page.create(db, page_in=page_in, created_by=current_user.id)
    return page


@router.get("/workspace/{workspace_id}/tree", response_model=List[PageTree])
def get_page_tree(
    workspace_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get hierarchical tree of pages"""
    # Check if user is a member of the workspace
    if not crud_workspace.is_member(db, workspace_id=workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )
    
    def build_tree(parent_id: Optional[UUID] = None) -> List[PageTree]:
        pages = crud_page.get_tree(db, workspace_id=workspace_id, parent_id=parent_id)
        result = []
        for page in pages:
            page_dict = PageTree.model_validate(page)
            page_dict.children = build_tree(parent_id=page.id)
            result.append(page_dict)
        return result
    
    return build_tree()


@router.get("/trash", response_model=List[PageResponse])
def list_trash(
    workspace_id: UUID = Query(..., description="Workspace ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all pages in trash (archived pages)"""
    # Check if user is a member of the workspace
    if not crud_workspace.is_member(db, workspace_id=workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )

    archived_pages = crud_page.get_archived(db, workspace_id=workspace_id)
    return archived_pages


@router.get("/{page_id}", response_model=PageWithBlocks)
def get_page(
    page_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get page details with blocks"""
    page = crud_page.get_by_id(db, page_id=page_id)
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
    
    return page


@router.patch("/{page_id}", response_model=PageResponse)
def update_page(
    page_id: UUID,
    page_in: PageUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update page metadata"""
    page = crud_page.get_by_id(db, page_id=page_id)
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
    
    updated_page = crud_page.update(db, page=page, page_in=page_in)
    return updated_page


@router.delete("/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_page(
    page_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Archive page (soft delete)"""
    page = crud_page.get_by_id(db, page_id=page_id)
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
    
    crud_page.archive(db, page=page)
    return None


@router.patch("/{page_id}/move", response_model=PageResponse)
def move_page(
    page_id: UUID,
    move_data: PageMove,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Move page to new parent and/or order"""
    page = crud_page.get_by_id(db, page_id=page_id)
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

    # If new_parent_id is provided, verify it exists and belongs to same workspace
    if move_data.new_parent_id:
        new_parent = crud_page.get_by_id(db, page_id=move_data.new_parent_id)
        if not new_parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New parent page not found"
            )
        if new_parent.workspace_id != page.workspace_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New parent must be in the same workspace"
            )
        # Prevent circular reference
        if new_parent.id == page.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot move page to itself"
            )

    moved_page = crud_page.move(db, page=page, move_data=move_data)
    return moved_page


@router.post("/{page_id}/restore", response_model=PageResponse)
def restore_page(
    page_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Restore page from trash"""
    page = crud_page.get_by_id(db, page_id=page_id)
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

    # Check if page is actually archived
    if not page.is_archived:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page is not in trash"
        )

    restored_page = crud_page.restore(db, page=page)
    return restored_page


@router.delete("/{page_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def delete_page_permanently(
    page_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Permanently delete page (cannot be undone)"""
    page = crud_page.get_by_id(db, page_id=page_id)
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

    # Optional: Only allow deletion if page is already archived
    if not page.is_archived:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be in trash before permanent deletion. Archive it first."
        )

    crud_page.delete(db, page=page)
    return None


@router.post("/{page_id}/duplicate", response_model=PageResponse, status_code=status.HTTP_201_CREATED)
def duplicate_page(
    page_id: UUID,
    include_blocks: bool = Query(True, description="Include blocks in duplication"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Duplicate a page with all its blocks"""
    page = crud_page.get_by_id(db, page_id=page_id)
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

    # Duplicate the page
    duplicated_page = crud_page.duplicate(
        db,
        page=page,
        created_by=current_user.id,
        include_blocks=include_blocks
    )
    return duplicated_page
