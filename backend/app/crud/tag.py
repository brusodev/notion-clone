"""
CRUD operations for Tags and PageTag relationships
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.tag import Tag, PageTag
from app.models.page import Page


# Tag CRUD operations

def create_tag(
    db: Session,
    name: str,
    workspace_id: UUID,
    created_by: UUID,
    color: Optional[str] = None
) -> Optional[Tag]:
    """
    Create a new tag in a workspace.
    Returns None if a tag with the same name already exists in the workspace.
    """
    try:
        tag = Tag(
            name=name,
            workspace_id=workspace_id,
            created_by=created_by,
            color=color
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag
    except IntegrityError:
        db.rollback()
        return None


def get_tag_by_id(db: Session, tag_id: UUID) -> Optional[Tag]:
    """Get a tag by its ID"""
    return db.query(Tag).filter(Tag.id == tag_id).first()


def get_workspace_tags(
    db: Session,
    workspace_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> List[Tag]:
    """Get all tags for a workspace, ordered by name"""
    return db.query(Tag).filter(
        Tag.workspace_id == workspace_id
    ).order_by(
        Tag.name
    ).offset(skip).limit(limit).all()


def update_tag(
    db: Session,
    tag_id: UUID,
    name: Optional[str] = None,
    color: Optional[str] = None
) -> Optional[Tag]:
    """
    Update a tag's name or color.
    Returns None if the tag doesn't exist or if updating would violate unique constraint.
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        return None

    try:
        if name is not None:
            tag.name = name
        if color is not None:
            tag.color = color
        tag.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(tag)
        return tag
    except IntegrityError:
        db.rollback()
        return None


def delete_tag(db: Session, tag_id: UUID) -> bool:
    """
    Delete a tag. This will also delete all PageTag relationships due to CASCADE.
    Returns True if deleted, False if tag didn't exist.
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        return False

    db.delete(tag)
    db.commit()
    return True


# PageTag CRUD operations

def add_tag_to_page(db: Session, page_id: UUID, tag_id: UUID) -> Optional[PageTag]:
    """
    Add a tag to a page.
    Returns None if the tag is already applied to the page.
    """
    try:
        page_tag = PageTag(page_id=page_id, tag_id=tag_id)
        db.add(page_tag)
        db.commit()
        db.refresh(page_tag)
        return page_tag
    except IntegrityError:
        db.rollback()
        return None


def remove_tag_from_page(db: Session, page_id: UUID, tag_id: UUID) -> bool:
    """
    Remove a tag from a page.
    Returns True if removed, False if the tag wasn't applied to the page.
    """
    page_tag = db.query(PageTag).filter(
        and_(
            PageTag.page_id == page_id,
            PageTag.tag_id == tag_id
        )
    ).first()

    if not page_tag:
        return False

    db.delete(page_tag)
    db.commit()
    return True


def get_page_tags(db: Session, page_id: UUID) -> List[Tag]:
    """Get all tags for a specific page, ordered by tag name"""
    return db.query(Tag).join(
        PageTag,
        Tag.id == PageTag.tag_id
    ).filter(
        PageTag.page_id == page_id
    ).order_by(
        Tag.name
    ).all()


def get_pages_by_tag(
    db: Session,
    tag_id: UUID,
    workspace_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> List[Page]:
    """
    Get all pages with a specific tag in a workspace.
    Only returns non-archived pages, ordered by title.
    """
    return db.query(Page).join(
        PageTag,
        Page.id == PageTag.page_id
    ).filter(
        and_(
            PageTag.tag_id == tag_id,
            Page.workspace_id == workspace_id,
            Page.is_archived == False
        )
    ).order_by(
        Page.title
    ).offset(skip).limit(limit).all()


def is_tag_on_page(db: Session, page_id: UUID, tag_id: UUID) -> bool:
    """Check if a tag is applied to a page"""
    page_tag = db.query(PageTag).filter(
        and_(
            PageTag.page_id == page_id,
            PageTag.tag_id == tag_id
        )
    ).first()
    return page_tag is not None


def get_tag_count_for_workspace(db: Session, workspace_id: UUID) -> int:
    """Get total count of tags in a workspace"""
    return db.query(Tag).filter(Tag.workspace_id == workspace_id).count()


def get_page_count_for_tag(db: Session, tag_id: UUID) -> int:
    """Get count of pages that have a specific tag"""
    return db.query(PageTag).filter(PageTag.tag_id == tag_id).count()
