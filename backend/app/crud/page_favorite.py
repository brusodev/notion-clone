from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from uuid import UUID
from app.models.page_favorite import PageFavorite
from app.models.page import Page


def add_favorite(db: Session, user_id: UUID, page_id: UUID) -> Optional[PageFavorite]:
    """
    Add a page to user's favorites.
    Returns None if the favorite already exists (prevents duplicates).
    """
    try:
        favorite = PageFavorite(user_id=user_id, page_id=page_id)
        db.add(favorite)
        db.commit()
        db.refresh(favorite)
        return favorite
    except IntegrityError:
        db.rollback()
        return None


def remove_favorite(db: Session, user_id: UUID, page_id: UUID) -> bool:
    """
    Remove a page from user's favorites.
    Returns True if favorite was removed, False if it didn't exist.
    """
    favorite = db.query(PageFavorite).filter(
        PageFavorite.user_id == user_id,
        PageFavorite.page_id == page_id
    ).first()

    if not favorite:
        return False

    db.delete(favorite)
    db.commit()
    return True


def get_user_favorites(db: Session, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Page]:
    """
    Get all favorited pages for a user.
    Returns list of Page objects ordered by when they were favorited (most recent first).
    """
    favorites = db.query(Page).join(
        PageFavorite,
        Page.id == PageFavorite.page_id
    ).filter(
        PageFavorite.user_id == user_id,
        Page.is_archived == False
    ).order_by(
        PageFavorite.created_at.desc()
    ).offset(skip).limit(limit).all()

    return favorites


def is_favorited(db: Session, user_id: UUID, page_id: UUID) -> bool:
    """
    Check if a page is favorited by a user.
    """
    favorite = db.query(PageFavorite).filter(
        PageFavorite.user_id == user_id,
        PageFavorite.page_id == page_id
    ).first()

    return favorite is not None


def get_favorites_count(db: Session, user_id: UUID) -> int:
    """
    Get total count of favorited pages for a user.
    """
    return db.query(PageFavorite).filter(
        PageFavorite.user_id == user_id
    ).count()
