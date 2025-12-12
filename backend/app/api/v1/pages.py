from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.api.deps import get_db, get_current_active_user
from app.crud import page as crud_page
from app.crud import workspace as crud_workspace
from app.crud import page_version as crud_page_version
from app.crud import page_favorite as crud_page_favorite
from app.schemas.page import PageCreate, PageUpdate, PageMove, PageResponse, PageWithBlocks, PageTree
from app.schemas.page_version import PageVersionResponse, PageVersionListItem
from app.schemas.page_favorite import PageFavoriteResponse, PageFavoriteStatus
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


# ==================== FAVORITES ====================


@router.get("/favorites", response_model=List[PageResponse])
def get_favorites(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all favorited pages for the current user"""
    pages = crud_page_favorite.get_user_favorites(db, user_id=current_user.id, skip=skip, limit=limit)
    return pages


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
    change_summary: Optional[str] = Query(None, description="Summary of changes for version history"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update page metadata (automatically creates a version if significant changes)"""
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

    updated_page = crud_page.update(
        db,
        page=page,
        page_in=page_in,
        created_by=current_user.id,
        change_summary=change_summary
    )
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


@router.get("/{page_id}/versions", response_model=List[PageVersionListItem])
def list_page_versions(
    page_id: UUID,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of versions to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all versions of a page"""
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

    versions = crud_page_version.get_versions(db, page_id=page_id, limit=limit)

    # Convert to PageVersionListItem with blocks_count
    result = []
    for version in versions:
        version_data = {
            "id": version.id,
            "version_number": version.version_number,
            "title": version.title,
            "created_at": version.created_at,
            "created_by": version.created_by,
            "change_summary": version.change_summary,
            "blocks_count": len(version.content_snapshot)
        }
        result.append(PageVersionListItem(**version_data))

    return result


@router.get("/{page_id}/versions/{version_number}", response_model=PageVersionResponse)
def get_page_version(
    page_id: UUID,
    version_number: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific version of a page"""
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

    version = crud_page_version.get_version(db, page_id=page_id, version_number=version_number)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )

    return version


@router.post("/{page_id}/versions/{version_number}/restore", response_model=PageResponse)
def restore_page_version(
    page_id: UUID,
    version_number: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Restore a page to a specific version"""
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

    version = crud_page_version.get_version(db, page_id=page_id, version_number=version_number)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )

    # Create a new version before restoring (to preserve current state)
    crud_page_version.create_version(
        db=db,
        page=page,
        created_by=current_user.id,
        change_summary=f"Before restoring to version {version_number}"
    )

    # Restore page metadata
    page.title = version.title
    page.icon = version.icon
    page.cover_image = version.cover_image

    # Delete current blocks
    from app.models.block import Block
    db.query(Block).filter(Block.page_id == page_id).delete()

    # Restore blocks from snapshot
    block_id_map = {}  # Map old IDs to new IDs for parent_block_id references

    for block_data in version.content_snapshot:
        from uuid import uuid4
        old_id = UUID(block_data["id"])
        new_id = uuid4()
        block_id_map[old_id] = new_id

        new_block = Block(
            id=new_id,
            page_id=page_id,
            type=block_data["type"],
            content=block_data["content"],
            order=block_data["order"],
            parent_block_id=None  # Will be set in second pass
        )
        db.add(new_block)

    db.flush()

    # Second pass: restore parent_block_id references
    for block_data in version.content_snapshot:
        if block_data.get("parent_block_id"):
            old_id = UUID(block_data["id"])
            old_parent_id = UUID(block_data["parent_block_id"])
            new_id = block_id_map.get(old_id)
            new_parent_id = block_id_map.get(old_parent_id)

            if new_id and new_parent_id:
                block = db.query(Block).filter(Block.id == new_id).first()
                if block:
                    block.parent_block_id = new_parent_id

    db.commit()
    db.refresh(page)
    return page


@router.post("/{page_id}/favorite", response_model=PageFavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(
    page_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a page to favorites"""
    # Check if page exists
    page = crud_page.get_by_id(db, page_id=page_id)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )

    # Check if user has access to the page (must be workspace member)
    if not crud_workspace.is_member(db, workspace_id=page.workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )

    # Add to favorites
    favorite = crud_page_favorite.add_favorite(db, user_id=current_user.id, page_id=page_id)
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Page is already in favorites"
        )

    return favorite


@router.delete("/{page_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    page_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove a page from favorites"""
    removed = crud_page_favorite.remove_favorite(db, user_id=current_user.id, page_id=page_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not in favorites"
        )


@router.get("/{page_id}/favorite", response_model=PageFavoriteStatus)
def check_favorite_status(
    page_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check if a page is favorited by the current user"""
    from app.models.page_favorite import PageFavorite

    is_favorited = crud_page_favorite.is_favorited(db, user_id=current_user.id, page_id=page_id)

    favorited_at = None
    if is_favorited:
        favorite = db.query(PageFavorite).filter(
            PageFavorite.user_id == current_user.id,
            PageFavorite.page_id == page_id
        ).first()
        if favorite:
            favorited_at = favorite.created_at

    return PageFavoriteStatus(is_favorited=is_favorited, favorited_at=favorited_at)
