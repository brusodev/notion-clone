"""
Permission service for checking user access to pages.
This service provides centralized permission checking logic.
"""

from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from app.models.page_permission import PermissionLevel
from app.models.page import Page
from app.models.workspace_member import WorkspaceMember, WorkspaceRole
from app.crud import page_permission as permission_crud


class PermissionService:
    """Service for managing and checking page permissions"""

    @staticmethod
    def check_page_access(
        db: Session,
        page_id: UUID,
        user_id: UUID,
        required_level: PermissionLevel
    ) -> bool:
        """
        Check if a user has access to a page.

        Access is granted if:
        1. User is the page creator, OR
        2. User is a workspace admin/owner, OR
        3. User has explicit page permission at the required level or higher

        Args:
            db: Database session
            page_id: ID of the page to check
            user_id: ID of the user requesting access
            required_level: Minimum permission level required

        Returns:
            True if user has access, False otherwise
        """
        # Get the page
        page = db.query(Page).filter(Page.id == page_id).first()
        if not page:
            return False

        # Check if user is the page creator
        if page.created_by == user_id:
            return True

        # Check if user is workspace admin/owner
        workspace_member = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == page.workspace_id,
            WorkspaceMember.user_id == user_id
        ).first()

        if workspace_member and workspace_member.role in [WorkspaceRole.ADMIN, WorkspaceRole.OWNER]:
            return True

        # Check explicit page permission
        return permission_crud.has_permission(db, page_id, user_id, required_level)

    @staticmethod
    def require_page_access(
        db: Session,
        page_id: UUID,
        user_id: UUID,
        required_level: PermissionLevel
    ) -> Page:
        """
        Require user has access to a page, or raise 403 Forbidden.

        Args:
            db: Database session
            page_id: ID of the page to check
            user_id: ID of the user requesting access
            required_level: Minimum permission level required

        Returns:
            The Page object if access is granted

        Raises:
            HTTPException 404 if page not found
            HTTPException 403 if user doesn't have required access
        """
        # Get the page
        page = db.query(Page).filter(Page.id == page_id).first()
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page not found"
            )

        # Check if user has access
        has_access = PermissionService.check_page_access(
            db, page_id, user_id, required_level
        )

        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have permission to {required_level.value} this page"
            )

        return page

    @staticmethod
    def can_manage_permissions(
        db: Session,
        page_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Check if a user can manage (grant/revoke) permissions for a page.

        Only page creators and workspace admins/owners can manage permissions.

        Args:
            db: Database session
            page_id: ID of the page
            user_id: ID of the user

        Returns:
            True if user can manage permissions, False otherwise
        """
        # Get the page
        page = db.query(Page).filter(Page.id == page_id).first()
        if not page:
            return False

        # Check if user is the page creator
        if page.created_by == user_id:
            return True

        # Check if user is workspace admin/owner
        workspace_member = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == page.workspace_id,
            WorkspaceMember.user_id == user_id
        ).first()

        return workspace_member and workspace_member.role in [WorkspaceRole.ADMIN, WorkspaceRole.OWNER]

    @staticmethod
    def require_permission_management(
        db: Session,
        page_id: UUID,
        user_id: UUID
    ) -> Page:
        """
        Require user can manage permissions for a page, or raise 403 Forbidden.

        Args:
            db: Database session
            page_id: ID of the page
            user_id: ID of the user

        Returns:
            The Page object if user can manage permissions

        Raises:
            HTTPException 404 if page not found
            HTTPException 403 if user can't manage permissions
        """
        # Get the page
        page = db.query(Page).filter(Page.id == page_id).first()
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Page not found"
            )

        # Check if user can manage permissions
        if not PermissionService.can_manage_permissions(db, page_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to manage access to this page"
            )

        return page

    @staticmethod
    def get_user_permission_level(
        db: Session,
        page_id: UUID,
        user_id: UUID
    ) -> PermissionLevel | None:
        """
        Get the effective permission level for a user on a page.

        Returns the highest permission level from:
        - EDIT if user is creator or workspace admin/owner
        - Explicit permission level if granted
        - None if no access

        Args:
            db: Database session
            page_id: ID of the page
            user_id: ID of the user

        Returns:
            PermissionLevel or None
        """
        # Get the page
        page = db.query(Page).filter(Page.id == page_id).first()
        if not page:
            return None

        # Check if user is the page creator - has EDIT access
        if page.created_by == user_id:
            return PermissionLevel.EDIT

        # Check if user is workspace admin/owner - has EDIT access
        workspace_member = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == page.workspace_id,
            WorkspaceMember.user_id == user_id
        ).first()

        if workspace_member and workspace_member.role in [WorkspaceRole.ADMIN, WorkspaceRole.OWNER]:
            return PermissionLevel.EDIT

        # Get explicit page permission
        permission = permission_crud.get_user_permission(db, page_id, user_id)
        return permission.permission_level if permission else None
