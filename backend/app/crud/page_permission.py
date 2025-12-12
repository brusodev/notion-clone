from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from uuid import UUID
from app.models.page_permission import PagePermission, PermissionLevel
from app.models.user import User


def grant_permission(
    db: Session,
    page_id: UUID,
    user_id: UUID,
    permission_level: PermissionLevel,
    granted_by: UUID
) -> Optional[PagePermission]:
    """
    Grant permission to a user for a page.
    Returns None if the permission already exists (prevents duplicates).
    """
    try:
        permission = PagePermission(
            page_id=page_id,
            user_id=user_id,
            permission_level=permission_level,
            granted_by=granted_by
        )
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission
    except IntegrityError:
        db.rollback()
        return None


def update_permission(
    db: Session,
    page_id: UUID,
    user_id: UUID,
    permission_level: PermissionLevel
) -> Optional[PagePermission]:
    """
    Update an existing permission level.
    Returns None if the permission doesn't exist.
    """
    permission = db.query(PagePermission).filter(
        PagePermission.page_id == page_id,
        PagePermission.user_id == user_id
    ).first()

    if not permission:
        return None

    permission.permission_level = permission_level
    db.commit()
    db.refresh(permission)
    return permission


def revoke_permission(db: Session, page_id: UUID, user_id: UUID) -> bool:
    """
    Revoke a user's permission for a page.
    Returns True if permission was revoked, False if it didn't exist.
    """
    permission = db.query(PagePermission).filter(
        PagePermission.page_id == page_id,
        PagePermission.user_id == user_id
    ).first()

    if not permission:
        return False

    db.delete(permission)
    db.commit()
    return True


def get_page_permissions(
    db: Session,
    page_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> List[PagePermission]:
    """
    Get all permissions for a page.
    Returns list of PagePermission objects with user information.
    """
    return db.query(PagePermission).filter(
        PagePermission.page_id == page_id
    ).offset(skip).limit(limit).all()


def get_user_permission(
    db: Session,
    page_id: UUID,
    user_id: UUID
) -> Optional[PagePermission]:
    """
    Get a specific user's permission for a page.
    Returns None if no permission exists.
    """
    return db.query(PagePermission).filter(
        PagePermission.page_id == page_id,
        PagePermission.user_id == user_id
    ).first()


def get_user_shared_pages(
    db: Session,
    user_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> List[PagePermission]:
    """
    Get all pages that have been shared with a user.
    Returns list of PagePermission objects.
    """
    return db.query(PagePermission).filter(
        PagePermission.user_id == user_id
    ).offset(skip).limit(limit).all()


def has_permission(
    db: Session,
    page_id: UUID,
    user_id: UUID,
    required_level: PermissionLevel
) -> bool:
    """
    Check if a user has at least the required permission level for a page.

    Permission hierarchy: VIEW < COMMENT < EDIT
    If user has EDIT, they also have COMMENT and VIEW.
    If user has COMMENT, they also have VIEW.
    """
    permission = get_user_permission(db, page_id, user_id)

    if not permission:
        return False

    # Map permission levels to hierarchy
    level_hierarchy = {
        PermissionLevel.VIEW: 1,
        PermissionLevel.COMMENT: 2,
        PermissionLevel.EDIT: 3
    }

    user_level = level_hierarchy.get(permission.permission_level, 0)
    required_level_value = level_hierarchy.get(required_level, 0)

    return user_level >= required_level_value


def can_view(db: Session, page_id: UUID, user_id: UUID) -> bool:
    """Check if user can view a page."""
    return has_permission(db, page_id, user_id, PermissionLevel.VIEW)


def can_comment(db: Session, page_id: UUID, user_id: UUID) -> bool:
    """Check if user can comment on a page."""
    return has_permission(db, page_id, user_id, PermissionLevel.COMMENT)


def can_edit(db: Session, page_id: UUID, user_id: UUID) -> bool:
    """Check if user can edit a page."""
    return has_permission(db, page_id, user_id, PermissionLevel.EDIT)


def get_permissions_count(db: Session, page_id: UUID) -> int:
    """Get total count of permissions for a page."""
    return db.query(PagePermission).filter(
        PagePermission.page_id == page_id
    ).count()


def revoke_all_permissions(db: Session, page_id: UUID) -> int:
    """
    Revoke all permissions for a page.
    Returns the number of permissions revoked.
    """
    count = db.query(PagePermission).filter(
        PagePermission.page_id == page_id
    ).delete()
    db.commit()
    return count
