from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from uuid import UUID, uuid4
from app.models.page import Page
from app.models.block import Block
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


def get_archived(db: Session, workspace_id: UUID) -> List[Page]:
    """Get all archived pages in a workspace (trash)"""
    return db.query(Page).filter(
        Page.workspace_id == workspace_id,
        Page.is_archived == True
    ).order_by(Page.updated_at.desc()).all()


def restore(db: Session, page: Page) -> Page:
    """Restore page from trash"""
    page.is_archived = False
    db.commit()
    db.refresh(page)
    return page


def delete(db: Session, page: Page) -> None:
    """Permanently delete page"""
    db.delete(page)
    db.commit()


def duplicate(db: Session, page: Page, created_by: UUID, include_blocks: bool = True) -> Page:
    """Duplicate a page with all its blocks"""
    # Create new page with copied attributes
    new_page = Page(
        workspace_id=page.workspace_id,
        parent_id=page.parent_id,
        title=f"{page.title} (Copy)",
        icon=page.icon,
        cover_image=page.cover_image,
        is_archived=False,  # New copy should not be archived
        is_public=False,    # New copy should not be public
        order=page.order,
        created_by=created_by
    )
    db.add(new_page)
    db.flush()  # Get the new page ID

    # Duplicate blocks if requested
    if include_blocks:
        # Get all blocks from original page
        original_blocks = db.query(Block).filter(
            Block.page_id == page.id
        ).order_by(Block.order).all()

        # Map old block IDs to new block IDs (for parent_block_id references)
        block_id_mapping: Dict[UUID, UUID] = {}

        # First pass: create all blocks with new IDs
        for original_block in original_blocks:
            new_block_id = uuid4()
            block_id_mapping[original_block.id] = new_block_id

            new_block = Block(
                id=new_block_id,
                page_id=new_page.id,
                parent_block_id=None,  # Will be updated in second pass
                type=original_block.type,
                content=original_block.content.copy() if original_block.content else {},
                order=original_block.order
            )
            db.add(new_block)

        db.flush()

        # Second pass: update parent_block_id references
        for original_block in original_blocks:
            if original_block.parent_block_id:
                new_block_id = block_id_mapping[original_block.id]
                new_parent_id = block_id_mapping.get(original_block.parent_block_id)

                if new_parent_id:
                    new_block = db.query(Block).filter(Block.id == new_block_id).first()
                    if new_block:
                        new_block.parent_block_id = new_parent_id

    db.commit()
    db.refresh(new_page)
    return new_page
