from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from uuid import UUID

from app.models.comment_reaction import CommentReaction
from app.schemas.comment import ReactionCreate


def add_reaction(
    db: Session,
    comment_id: UUID,
    user_id: UUID,
    reaction_in: ReactionCreate
) -> Optional[CommentReaction]:
    """
    Add a reaction to a comment.
    Returns None if reaction already exists (duplicate).
    """
    reaction = CommentReaction(
        comment_id=comment_id,
        user_id=user_id,
        reaction_type=reaction_in.reaction_type
    )

    try:
        db.add(reaction)
        db.commit()
        db.refresh(reaction)
        return reaction
    except IntegrityError:
        # Duplicate reaction (comment_id, user_id, reaction_type) already exists
        db.rollback()
        return None


def remove_reaction(
    db: Session,
    comment_id: UUID,
    user_id: UUID,
    reaction_type: str
) -> bool:
    """
    Remove a reaction from a comment.
    Returns True if reaction was removed, False if not found.
    """
    result = db.query(CommentReaction).filter(
        CommentReaction.comment_id == comment_id,
        CommentReaction.user_id == user_id,
        CommentReaction.reaction_type == reaction_type
    ).delete()

    db.commit()
    return result > 0


def get_user_reaction(
    db: Session,
    comment_id: UUID,
    user_id: UUID,
    reaction_type: str
) -> Optional[CommentReaction]:
    """
    Check if user has a specific reaction on a comment.
    Returns the reaction if exists, None otherwise.
    """
    return db.query(CommentReaction).filter(
        CommentReaction.comment_id == comment_id,
        CommentReaction.user_id == user_id,
        CommentReaction.reaction_type == reaction_type
    ).first()


def get_all_user_reactions(
    db: Session,
    comment_id: UUID,
    user_id: UUID
) -> list[CommentReaction]:
    """
    Get all reactions by a user on a comment.
    """
    return db.query(CommentReaction).filter(
        CommentReaction.comment_id == comment_id,
        CommentReaction.user_id == user_id
    ).all()
