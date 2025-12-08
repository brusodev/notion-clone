from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.api.deps import get_db, get_current_active_user
from app.crud import block as crud_block
from app.crud import page as crud_page
from app.crud import workspace as crud_workspace
from app.schemas.block import BlockCreate, BlockUpdate, BlockMove, BlockResponse
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=BlockResponse, status_code=status.HTTP_201_CREATED)
def create_block(
    block_in: BlockCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new block"""
    # Get the page
    page = crud_page.get_by_id(db, page_id=block_in.page_id)
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
    
    # If parent_block_id is provided, verify it exists and belongs to same page
    if block_in.parent_block_id:
        parent_block = crud_block.get_by_id(db, block_id=block_in.parent_block_id)
        if not parent_block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent block not found"
            )
        if parent_block.page_id != block_in.page_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent block must be on the same page"
            )
    
    block = crud_block.create(db, block_in=block_in)
    return block


@router.get("/page/{page_id}", response_model=List[BlockResponse])
def list_blocks(
    page_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all blocks in a page (ordered)"""
    # Get the page
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
    
    blocks = crud_block.get_by_page(db, page_id=page_id)
    return blocks


@router.get("/{block_id}", response_model=BlockResponse)
def get_block(
    block_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get block by ID"""
    block = crud_block.get_by_id(db, block_id=block_id)
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found"
        )

    # Get the page
    page = crud_page.get_by_id(db, page_id=block.page_id)
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

    return block


@router.patch("/{block_id}", response_model=BlockResponse)
def update_block(
    block_id: UUID,
    block_in: BlockUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update block content or type"""
    block = crud_block.get_by_id(db, block_id=block_id)
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found"
        )

    # Get the page
    page = crud_page.get_by_id(db, page_id=block.page_id)
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

    updated_block = crud_block.update(db, block=block, block_in=block_in)
    return updated_block


@router.delete("/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_block(
    block_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete block"""
    block = crud_block.get_by_id(db, block_id=block_id)
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found"
        )
    
    # Get the page
    page = crud_page.get_by_id(db, page_id=block.page_id)
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
    
    crud_block.delete(db, block=block)
    return None


@router.patch("/{block_id}/move", response_model=BlockResponse)
def move_block(
    block_id: UUID,
    move_data: BlockMove,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Reorder block and/or change parent"""
    block = crud_block.get_by_id(db, block_id=block_id)
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found"
        )
    
    # Get the page
    page = crud_page.get_by_id(db, page_id=block.page_id)
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
    
    # If new_parent_block_id is provided, verify it exists and belongs to same page
    if move_data.new_parent_block_id:
        new_parent = crud_block.get_by_id(db, block_id=move_data.new_parent_block_id)
        if not new_parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New parent block not found"
            )
        if new_parent.page_id != block.page_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New parent must be on the same page"
            )
        # Prevent circular reference
        if new_parent.id == block.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot move block to itself"
            )
    
    moved_block = crud_block.move(db, block=block, move_data=move_data)
    return moved_block
