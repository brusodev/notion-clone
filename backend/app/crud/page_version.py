from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.page_version import PageVersion
from app.models.page import Page
from app.models.block import Block


def create_version(
    db: Session,
    page: Page,
    created_by: UUID,
    change_summary: Optional[str] = None
) -> PageVersion:
    """Create a new version snapshot of a page"""

    # Get current version number
    last_version = db.query(PageVersion).filter(
        PageVersion.page_id == page.id
    ).order_by(PageVersion.version_number.desc()).first()

    version_number = 1 if not last_version else last_version.version_number + 1

    # Capture all blocks as snapshot
    blocks = db.query(Block).filter(Block.page_id == page.id).order_by(Block.order).all()
    content_snapshot = [
        {
            "id": str(block.id),
            "type": block.type,
            "content": block.content,
            "order": block.order,
            "parent_block_id": str(block.parent_block_id) if block.parent_block_id else None
        }
        for block in blocks
    ]

    # Create version
    version = PageVersion(
        page_id=page.id,
        version_number=version_number,
        title=page.title,
        icon=page.icon,
        cover_image=page.cover_image,
        content_snapshot=content_snapshot,
        created_by=created_by,
        change_summary=change_summary
    )

    db.add(version)
    db.commit()
    db.refresh(version)
    return version


def get_versions(db: Session, page_id: UUID, limit: int = 50) -> List[PageVersion]:
    """Get all versions of a page"""
    return db.query(PageVersion).filter(
        PageVersion.page_id == page_id
    ).order_by(PageVersion.version_number.desc()).limit(limit).all()


def get_version(db: Session, page_id: UUID, version_number: int) -> Optional[PageVersion]:
    """Get a specific version of a page"""
    return db.query(PageVersion).filter(
        PageVersion.page_id == page_id,
        PageVersion.version_number == version_number
    ).first()


def get_version_by_id(db: Session, version_id: UUID) -> Optional[PageVersion]:
    """Get version by ID"""
    return db.query(PageVersion).filter(PageVersion.id == version_id).first()
