from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from uuid import UUID

from app.models.comment_attachment import CommentAttachment
from app.schemas.comment import AttachmentCreate


def create(
    db: Session,
    comment_id: UUID,
    attachment_in: AttachmentCreate,
    uploaded_by: UUID
) -> CommentAttachment:
    """
    Create a new attachment for a comment.
    """
    attachment = CommentAttachment(
        comment_id=comment_id,
        file_name=attachment_in.file_name,
        file_url=attachment_in.file_url,
        file_size=attachment_in.file_size,
        mime_type=attachment_in.mime_type,
        uploaded_by=uploaded_by,
        order_index=attachment_in.order_index
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


def get_by_id(db: Session, attachment_id: UUID) -> Optional[CommentAttachment]:
    """Get attachment by ID with uploader info"""
    return db.query(CommentAttachment).options(
        joinedload(CommentAttachment.uploader)
    ).filter(CommentAttachment.id == attachment_id).first()


def get_by_comment(db: Session, comment_id: UUID) -> List[CommentAttachment]:
    """Get all attachments for a comment, ordered by order_index"""
    return db.query(CommentAttachment).options(
        joinedload(CommentAttachment.uploader)
    ).filter(
        CommentAttachment.comment_id == comment_id
    ).order_by(CommentAttachment.order_index).all()


def delete(db: Session, attachment: CommentAttachment) -> None:
    """Permanently delete attachment"""
    db.delete(attachment)
    db.commit()


def update_order(
    db: Session,
    attachment: CommentAttachment,
    new_order: int
) -> CommentAttachment:
    """Update attachment order"""
    attachment.order_index = new_order
    db.commit()
    db.refresh(attachment)
    return attachment
