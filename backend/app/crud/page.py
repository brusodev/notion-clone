from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.page import Page
from app.schemas.page import PageCreate, PageUpdate, PageMove


def create(db: Session, page_in: PageCreate, created_by: UUID) -> Page:
    """Create a new page"""
    page = Page(
        workspace_id=page_in.workspace_id,
        parent_id=page_in.parent_id,
        title=page_in.title,
        icon=page_in.icon,
        cover_image=page_in.cover_image,
        order=page_in.order,
        created_by=created_by
    )
    db.add(page)
    db.commit()
    db.refresh(page)
    return page


def get_by_id(db: Session, page_id: UUID) -> Optional[Page]:
    """Get page by ID"""
    return db.query(Page).filter(Page.id == page_id).first()


def get_by_workspace(db: Session, workspace_id: UUID, include_archived: bool = False) -> List[Page]:
    """Get all pages in a workspace"""
    query = db.query(Page).filter(Page.workspace_id == workspace_id)
    if not include_archived:
        query = query.filter(Page.is_archived == False)
    return query.order_by(Page.order).all()


def get_tree(db: Session, workspace_id: UUID, parent_id: Optional[UUID] = None) -> List[Page]:
    """Get hierarchical tree of pages"""
    query = db.query(Page).filter(
        Page.workspace_id == workspace_id,
        Page.is_archived == False,
        Page.parent_id == parent_id
    )
    return query.order_by(Page.order).all()


def update(db: Session, page: Page, page_in: PageUpdate) -> Page:
    """Update page"""
    update_data = page_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(page, field, value)
    db.commit()
    db.refresh(page)
    return page


def archive(db: Session, page: Page) -> Page:
    """Archive page (soft delete)"""
    page.is_archived = True
    db.commit()
    db.refresh(page)
    return page


def move(db: Session, page: Page, move_data: PageMove) -> Page:
    """Move page to new parent and/or order"""
    page.parent_id = move_data.new_parent_id
    page.order = move_data.new_order
    db.commit()
    db.refresh(page)
    return page


def delete(db: Session, page: Page) -> None:
    """Permanently delete page"""
    db.delete(page)
    db.commit()
