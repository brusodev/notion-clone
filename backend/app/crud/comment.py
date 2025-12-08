from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, and_, or_
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime
import re

from app.models.comment import Comment
from app.models.comment_mention import CommentMention
from app.models.comment_reaction import CommentReaction
from app.models.comment_attachment import CommentAttachment
from app.models.workspace_member import WorkspaceMember
from app.schemas.comment import CommentCreate, CommentUpdate, ReactionSummary


def _parse_mentions(content: str) -> List[UUID]:
    """
    Parse @mentions from comment content.
    Expected format: @[User Name](uuid)
    Returns list of unique mentioned user UUIDs.
    """
    # Regex pattern to match @[Name](uuid) format
    pattern = r'@\[([^\]]+)\]\(([a-f0-9-]{36})\)'
    matches = re.findall(pattern, content, re.IGNORECASE)

    # Extract UUIDs and ensure uniqueness
    uuids = []
    seen = set()
    for _, uuid_str in matches:
        try:
            uuid_obj = UUID(uuid_str)
            if uuid_obj not in seen:
                uuids.append(uuid_obj)
                seen.add(uuid_obj)
        except ValueError:
            # Invalid UUID, skip
            continue

    return uuids


def _calculate_thread_depth(db: Session, parent_comment_id: Optional[UUID]) -> int:
    """Calculate thread depth for a new comment"""
    if not parent_comment_id:
        return 0

    parent = db.query(Comment).filter(Comment.id == parent_comment_id).first()
    if not parent:
        return 0

    # Max depth is 5
    return min(parent.thread_depth + 1, 5)


def create(db: Session, comment_in: CommentCreate, author_id: UUID, workspace_id: UUID) -> Comment:
    """
    Create a new comment with automatic thread_depth calculation and mention parsing.
    Validates that mentioned users are members of the workspace.
    """
    # Calculate thread depth
    thread_depth = _calculate_thread_depth(db, comment_in.parent_comment_id)

    # Check if max depth reached
    if thread_depth >= 5 and comment_in.parent_comment_id:
        raise ValueError("Maximum thread depth (5) reached")

    # Create comment
    comment = Comment(
        page_id=comment_in.page_id,
        block_id=comment_in.block_id,
        parent_comment_id=comment_in.parent_comment_id,
        thread_depth=thread_depth,
        content=comment_in.content,
        author_id=author_id,
        is_deleted=False
    )
    db.add(comment)
    db.flush()  # Get comment.id without committing

    # Parse and create mentions
    mentioned_user_ids = _parse_mentions(comment_in.content)

    # Validate that mentioned users are workspace members
    for user_id in mentioned_user_ids:
        is_member = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id
        ).first() is not None

        if not is_member:
            # Skip invalid mentions (user not in workspace)
            continue

        mention = CommentMention(
            comment_id=comment.id,
            mentioned_user_id=user_id
        )
        db.add(mention)

    db.commit()
    db.refresh(comment)
    return comment


def get_by_id(
    db: Session,
    comment_id: UUID,
    include_deleted: bool = False
) -> Optional[Comment]:
    """
    Get comment by ID with eager loading to prevent N+1 queries.
    """
    query = db.query(Comment).options(
        joinedload(Comment.author),
        joinedload(Comment.deleted_by_user),
        selectinload(Comment.reactions).joinedload(CommentReaction.user),
        selectinload(Comment.mentions).joinedload(CommentMention.mentioned_user),
        selectinload(Comment.attachments).joinedload(CommentAttachment.uploader)
    ).filter(Comment.id == comment_id)

    if not include_deleted:
        query = query.filter(Comment.is_deleted == False)

    return query.first()


def get_by_page(
    db: Session,
    page_id: UUID,
    limit: int = 20,
    offset: int = 0,
    include_deleted: bool = False
) -> Tuple[List[Comment], int]:
    """
    Get top-level comments for a page with pagination.
    Returns (comments, total_count).
    """
    # Base query for top-level comments only
    base_query = db.query(Comment).filter(
        Comment.page_id == page_id,
        Comment.parent_comment_id.is_(None)
    )

    if not include_deleted:
        base_query = base_query.filter(Comment.is_deleted == False)

    # Count total
    total = base_query.count()

    # Get paginated results with eager loading
    comments = base_query.options(
        joinedload(Comment.author),
        joinedload(Comment.deleted_by_user),
        selectinload(Comment.reactions).joinedload(CommentReaction.user),
        selectinload(Comment.mentions).joinedload(CommentMention.mentioned_user),
        selectinload(Comment.attachments).joinedload(CommentAttachment.uploader),
        selectinload(Comment.replies).joinedload(Comment.author)  # Load first-level replies
    ).order_by(Comment.created_at.desc()).offset(offset).limit(limit).all()

    return comments, total


def get_by_block(
    db: Session,
    block_id: UUID,
    limit: int = 20,
    offset: int = 0,
    include_deleted: bool = False
) -> Tuple[List[Comment], int]:
    """
    Get top-level comments for a block with pagination.
    Returns (comments, total_count).
    """
    # Base query for top-level comments only
    base_query = db.query(Comment).filter(
        Comment.block_id == block_id,
        Comment.parent_comment_id.is_(None)
    )

    if not include_deleted:
        base_query = base_query.filter(Comment.is_deleted == False)

    # Count total
    total = base_query.count()

    # Get paginated results with eager loading
    comments = base_query.options(
        joinedload(Comment.author),
        joinedload(Comment.deleted_by_user),
        selectinload(Comment.reactions).joinedload(CommentReaction.user),
        selectinload(Comment.mentions).joinedload(CommentMention.mentioned_user),
        selectinload(Comment.attachments).joinedload(CommentAttachment.uploader),
        selectinload(Comment.replies).joinedload(Comment.author)  # Load first-level replies
    ).order_by(Comment.created_at.desc()).offset(offset).limit(limit).all()

    return comments, total


def update(db: Session, comment: Comment, comment_in: CommentUpdate) -> Comment:
    """
    Update comment content and re-parse mentions.
    """
    # Update content
    comment.content = comment_in.content
    comment.edited_at = datetime.utcnow()

    # Delete old mentions
    db.query(CommentMention).filter(CommentMention.comment_id == comment.id).delete()

    # Parse and create new mentions
    mentioned_user_ids = _parse_mentions(comment_in.content)
    for user_id in mentioned_user_ids:
        mention = CommentMention(
            comment_id=comment.id,
            mentioned_user_id=user_id
        )
        db.add(mention)

    db.commit()
    db.refresh(comment)
    return comment


def soft_delete(db: Session, comment: Comment, deleted_by: UUID) -> Comment:
    """
    Soft delete comment: mark as deleted and redact content.
    """
    comment.is_deleted = True
    comment.deleted_at = datetime.utcnow()
    comment.deleted_by = deleted_by
    comment.content = "[deleted]"

    db.commit()
    db.refresh(comment)
    return comment


def hard_delete(db: Session, comment: Comment) -> None:
    """
    Permanently delete comment (workspace owner only).
    Cascades to reactions, mentions, attachments, and replies.
    """
    db.delete(comment)
    db.commit()


def get_reaction_summary(
    db: Session,
    comment_id: UUID,
    current_user_id: Optional[UUID] = None
) -> List[ReactionSummary]:
    """
    Get aggregated reaction summary for a comment.
    Returns list of ReactionSummary with counts and user_reacted flag.
    """
    # Aggregate reactions by type
    reactions_query = db.query(
        CommentReaction.reaction_type,
        func.count(CommentReaction.id).label('count')
    ).filter(
        CommentReaction.comment_id == comment_id
    ).group_by(CommentReaction.reaction_type).all()

    # Check which reactions current user has
    user_reactions = set()
    if current_user_id:
        user_reactions_query = db.query(CommentReaction.reaction_type).filter(
            CommentReaction.comment_id == comment_id,
            CommentReaction.user_id == current_user_id
        ).all()
        user_reactions = {r.reaction_type for r in user_reactions_query}

    # Build summary
    summary = []
    for reaction_type, count in reactions_query:
        summary.append(ReactionSummary(
            reaction_type=reaction_type,
            count=count,
            user_reacted=(reaction_type in user_reactions)
        ))

    return summary


def get_replies_count(db: Session, comment_id: UUID) -> int:
    """Get count of replies for a comment"""
    return db.query(Comment).filter(
        Comment.parent_comment_id == comment_id,
        Comment.is_deleted == False
    ).count()
