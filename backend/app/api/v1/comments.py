from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.api.deps import get_db, get_current_active_user
from app.crud import comment as crud_comment
from app.crud import comment_reaction as crud_reaction
from app.crud import workspace as crud_workspace
from app.crud import page as crud_page
from app.crud import block as crud_block
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    CommentWithReplies,
    CommentListResponse,
    ReactionCreate,
    ReactionResponse,
    UserBasic,
    ReactionSummary,
)
from app.models.user import User
from app.models.workspace_member import WorkspaceRole

router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================

def _check_workspace_access(
    db: Session,
    user_id: UUID,
    page_id: Optional[UUID] = None,
    block_id: Optional[UUID] = None
) -> UUID:
    """
    Check if user has access to workspace via page or block.
    Returns workspace_id or raises 403/404.
    """
    if page_id:
        page = crud_page.get_by_id(db, page_id=page_id)
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page not found"
            )
        workspace_id = page.workspace_id
    elif block_id:
        block = crud_block.get_by_id(db, block_id=block_id)
        if not block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Block not found"
            )
        # Get page to get workspace_id
        page = crud_page.get_by_id(db, page_id=block.page_id)
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page not found"
            )
        workspace_id = page.workspace_id
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either page_id or block_id must be provided"
        )

    # Check workspace membership
    if not crud_workspace.is_member(db, workspace_id=workspace_id, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )

    return workspace_id


def _build_comment_response(
    comment,
    db: Session,
    current_user_id: UUID
) -> CommentResponse:
    """
    Build CommentResponse with all embedded data.
    """
    # Get reaction summary
    reactions = crud_comment.get_reaction_summary(
        db,
        comment_id=comment.id,
        current_user_id=current_user_id
    )

    # Get replies count
    replies_count = crud_comment.get_replies_count(db, comment_id=comment.id)

    # Build basic response
    response_data = {
        "id": comment.id,
        "page_id": comment.page_id,
        "block_id": comment.block_id,
        "parent_comment_id": comment.parent_comment_id,
        "thread_depth": comment.thread_depth,
        "content": comment.content,
        "author_id": comment.author_id,
        "is_deleted": comment.is_deleted,
        "deleted_at": comment.deleted_at,
        "deleted_by": comment.deleted_by,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at,
        "edited_at": comment.edited_at,
        "author": UserBasic.model_validate(comment.author) if comment.author else None,
        "deleted_by_user": UserBasic.model_validate(comment.deleted_by_user) if comment.deleted_by_user else None,
        "reactions": reactions,
        "mentioned_users": [UserBasic.model_validate(m.mentioned_user) for m in comment.mentions if m.mentioned_user],
        "attachments": [],  # TODO: Implement in Phase 5
        "replies_count": replies_count,
    }

    return CommentResponse(**response_data)


# ============================================================================
# Comment Endpoints
# ============================================================================

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new comment on a page or block.
    Automatically parses @mentions and calculates thread depth.
    """
    # Check workspace access
    _check_workspace_access(
        db,
        user_id=current_user.id,
        page_id=comment_in.page_id,
        block_id=comment_in.block_id
    )

    # If replying to a comment, validate parent exists
    if comment_in.parent_comment_id:
        parent = crud_comment.get_by_id(db, comment_id=comment_in.parent_comment_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found"
            )
        # Verify parent is on same page/block
        if parent.page_id != comment_in.page_id or parent.block_id != comment_in.block_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent comment must be on the same page/block"
            )

    # Create comment
    try:
        comment = crud_comment.create(
            db,
            comment_in=comment_in,
            author_id=current_user.id
        )
    except ValueError as e:
        # Max depth reached
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Reload with relationships
    comment = crud_comment.get_by_id(db, comment_id=comment.id)
    return _build_comment_response(comment, db, current_user.id)


@router.get("/page/{page_id}", response_model=CommentListResponse)
def list_comments_by_page(
    page_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List top-level comments for a page with pagination.
    """
    # Check workspace access
    _check_workspace_access(db, user_id=current_user.id, page_id=page_id)

    # Get comments
    offset = (page - 1) * page_size
    comments, total = crud_comment.get_by_page(
        db,
        page_id=page_id,
        limit=page_size,
        offset=offset
    )

    # Build responses
    comment_responses = [
        _build_comment_response(c, db, current_user.id)
        for c in comments
    ]

    return CommentListResponse(
        comments=comment_responses,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(offset + page_size) < total
    )


@router.get("/block/{block_id}", response_model=CommentListResponse)
def list_comments_by_block(
    block_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List top-level comments for a block with pagination.
    """
    # Check workspace access
    _check_workspace_access(db, user_id=current_user.id, block_id=block_id)

    # Get comments
    offset = (page - 1) * page_size
    comments, total = crud_comment.get_by_block(
        db,
        block_id=block_id,
        limit=page_size,
        offset=offset
    )

    # Build responses
    comment_responses = [
        _build_comment_response(c, db, current_user.id)
        for c in comments
    ]

    return CommentListResponse(
        comments=comment_responses,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(offset + page_size) < total
    )


@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(
    comment_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a single comment by ID with all embedded data.
    """
    comment = crud_comment.get_by_id(db, comment_id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Check workspace access
    _check_workspace_access(
        db,
        user_id=current_user.id,
        page_id=comment.page_id,
        block_id=comment.block_id
    )

    return _build_comment_response(comment, db, current_user.id)


@router.patch("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: UUID,
    comment_in: CommentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a comment (author only).
    Re-parses @mentions automatically.
    """
    comment = crud_comment.get_by_id(db, comment_id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Check workspace access
    _check_workspace_access(
        db,
        user_id=current_user.id,
        page_id=comment.page_id,
        block_id=comment.block_id
    )

    # Only author can edit
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the author can edit this comment"
        )

    # Update comment
    updated_comment = crud_comment.update(db, comment=comment, comment_in=comment_in)

    # Reload with relationships
    updated_comment = crud_comment.get_by_id(db, comment_id=updated_comment.id)
    return _build_comment_response(updated_comment, db, current_user.id)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: UUID,
    hard_delete: bool = Query(False, description="Permanently delete (owner only)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a comment.
    - Soft delete (default): Author or owner can soft delete (marks as deleted)
    - Hard delete: Owner only, permanently removes comment
    """
    comment = crud_comment.get_by_id(db, comment_id=comment_id, include_deleted=True)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Check workspace access
    workspace_id = _check_workspace_access(
        db,
        user_id=current_user.id,
        page_id=comment.page_id,
        block_id=comment.block_id
    )

    # Get user role
    user_role = crud_workspace.get_user_role(
        db,
        workspace_id=workspace_id,
        user_id=current_user.id
    )

    if hard_delete:
        # Only owner can hard delete
        if user_role != WorkspaceRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace owner can permanently delete comments"
            )
        crud_comment.hard_delete(db, comment=comment)
    else:
        # Author or owner can soft delete
        if comment.author_id != current_user.id and user_role != WorkspaceRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the author or workspace owner can delete this comment"
            )
        crud_comment.soft_delete(db, comment=comment, deleted_by=current_user.id)

    return None


# ============================================================================
# Reaction Endpoints
# ============================================================================

@router.post("/{comment_id}/reactions", response_model=ReactionResponse, status_code=status.HTTP_201_CREATED)
def add_reaction(
    comment_id: UUID,
    reaction_in: ReactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a reaction to a comment.
    Returns 200 if reaction already exists (idempotent).
    """
    comment = crud_comment.get_by_id(db, comment_id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Check workspace access
    _check_workspace_access(
        db,
        user_id=current_user.id,
        page_id=comment.page_id,
        block_id=comment.block_id
    )

    # Add reaction
    reaction = crud_reaction.add_reaction(
        db,
        comment_id=comment_id,
        user_id=current_user.id,
        reaction_in=reaction_in
    )

    if not reaction:
        # Reaction already exists, return existing one
        existing = crud_reaction.get_user_reaction(
            db,
            comment_id=comment_id,
            user_id=current_user.id,
            reaction_type=reaction_in.reaction_type
        )
        return ReactionResponse.model_validate(existing)

    return ReactionResponse.model_validate(reaction)


@router.delete("/{comment_id}/reactions/{reaction_type}", status_code=status.HTTP_204_NO_CONTENT)
def remove_reaction(
    comment_id: UUID,
    reaction_type: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove a reaction from a comment.
    """
    comment = crud_comment.get_by_id(db, comment_id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Check workspace access
    _check_workspace_access(
        db,
        user_id=current_user.id,
        page_id=comment.page_id,
        block_id=comment.block_id
    )

    # Remove reaction
    removed = crud_reaction.remove_reaction(
        db,
        comment_id=comment_id,
        user_id=current_user.id,
        reaction_type=reaction_type
    )

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reaction not found"
        )

    return None
