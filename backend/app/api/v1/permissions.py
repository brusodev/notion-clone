from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.api.deps import get_db, get_current_active_user
from app.crud import page_permission as crud_permission
from app.crud import user as crud_user
from app.services.permission_service import PermissionService
from app.schemas.page_permission import (
    PagePermissionCreate,
    PagePermissionUpdate,
    PagePermissionShareByEmail,
    PagePermissionResponse,
    PagePermissionListResponse,
    SharedPagesListResponse,
    SharedPageInfo,
    PermissionCheckResponse,
    UserInfo
)
from app.models.user import User
from app.models.page_permission import PermissionLevel

router = APIRouter()


@router.post("/{page_id}/share", response_model=PagePermissionResponse, status_code=status.HTTP_201_CREATED)
def grant_page_permission(
    page_id: UUID,
    permission_in: PagePermissionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Grant permission to a user for a page.
    Only page creators and workspace admins can grant permissions.
    """
    # Check if current user can manage permissions
    PermissionService.require_permission_management(db, page_id, current_user.id)

    # Check if target user exists
    target_user = crud_user.get_by_id(db, user_id=permission_in.user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Grant the permission
    permission = crud_permission.grant_permission(
        db,
        page_id=page_id,
        user_id=permission_in.user_id,
        permission_level=permission_in.permission_level,
        granted_by=current_user.id
    )

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Permission already exists. Use PUT to update."
        )

    return permission


@router.post("/{page_id}/share-by-email", response_model=PagePermissionResponse, status_code=status.HTTP_201_CREATED)
def grant_permission_by_email(
    page_id: UUID,
    permission_in: PagePermissionShareByEmail,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Grant permission to a user by email.
    Only page creators and workspace admins can grant permissions.
    """
    # Check if current user can manage permissions
    PermissionService.require_permission_management(db, page_id, current_user.id)

    # Find user by email
    target_user = crud_user.get_by_email(db, email=permission_in.email)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with email {permission_in.email}"
        )

    # Grant the permission
    permission = crud_permission.grant_permission(
        db,
        page_id=page_id,
        user_id=target_user.id,
        permission_level=permission_in.permission_level,
        granted_by=current_user.id
    )

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Permission already exists. Use PUT to update."
        )

    return permission


@router.put("/{page_id}/permissions/{user_id}", response_model=PagePermissionResponse)
def update_page_permission(
    page_id: UUID,
    user_id: UUID,
    permission_in: PagePermissionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing permission level.
    Only page creators and workspace admins can update permissions.
    """
    # Check if current user can manage permissions
    PermissionService.require_permission_management(db, page_id, current_user.id)

    # Update the permission
    permission = crud_permission.update_permission(
        db,
        page_id=page_id,
        user_id=user_id,
        permission_level=permission_in.permission_level
    )

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )

    return permission


@router.delete("/{page_id}/permissions/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_page_permission(
    page_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Revoke a user's permission for a page.
    Only page creators and workspace admins can revoke permissions.
    """
    # Check if current user can manage permissions
    PermissionService.require_permission_management(db, page_id, current_user.id)

    # Revoke the permission
    success = crud_permission.revoke_permission(db, page_id=page_id, user_id=user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )


@router.get("/{page_id}/permissions", response_model=PagePermissionListResponse)
def list_page_permissions(
    page_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all permissions for a page.
    Only page creators, workspace admins, and users with access can view permissions.
    """
    # Check if current user has at least view access to the page
    PermissionService.require_page_access(db, page_id, current_user.id, PermissionLevel.VIEW)

    # Get permissions
    permissions = crud_permission.get_page_permissions(db, page_id=page_id, skip=skip, limit=limit)
    total = crud_permission.get_permissions_count(db, page_id=page_id)

    return PagePermissionListResponse(
        total=total,
        permissions=permissions
    )


@router.get("/{page_id}/check-permission", response_model=PermissionCheckResponse)
def check_page_permission(
    page_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check current user's permission level for a page.
    """
    permission_level = PermissionService.get_user_permission_level(db, page_id, current_user.id)

    if not permission_level:
        return PermissionCheckResponse(
            has_permission=False,
            permission_level=None,
            can_view=False,
            can_comment=False,
            can_edit=False
        )

    return PermissionCheckResponse(
        has_permission=True,
        permission_level=permission_level,
        can_view=True,
        can_comment=permission_level in [PermissionLevel.COMMENT, PermissionLevel.EDIT],
        can_edit=permission_level == PermissionLevel.EDIT
    )


@router.get("/shared-with-me", response_model=SharedPagesListResponse)
def list_shared_pages(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all pages that have been shared with the current user.
    """
    permissions = crud_permission.get_user_shared_pages(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

    # Build response with page information
    shared_pages = []
    for perm in permissions:
        shared_pages.append(
            SharedPageInfo(
                id=perm.id,
                page_id=perm.page_id,
                permission_level=perm.permission_level,
                created_at=perm.created_at,
                page_title=perm.page.title if perm.page else None
            )
        )

    return SharedPagesListResponse(
        total=len(permissions),
        shared_pages=shared_pages
    )
