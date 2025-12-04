from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.api.deps import get_db, get_current_active_user
from app.crud import workspace as crud_workspace
from app.crud import invitation as crud_invitation
from app.crud import user as crud_user
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse
from app.schemas.invitation import (
    InvitationCreate,
    InvitationResponse,
    InvitationAccept,
    MemberUpdateRole,
    MemberResponse
)
from app.models.user import User
from app.models.workspace_member import WorkspaceRole
from app.core.email import email_service

router = APIRouter()


@router.get("/", response_model=List[WorkspaceResponse])
def list_workspaces(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all workspaces where user is a member"""
    workspaces = crud_workspace.get_by_user(db, user_id=current_user.id)
    return workspaces


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    workspace_in: WorkspaceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new workspace"""
    workspace = crud_workspace.create(db, workspace_in=workspace_in, owner_id=current_user.id)
    return workspace


# Member Management Endpoints (must come BEFORE generic /{workspace_id} routes)

@router.get("/{workspace_id}/members", response_model=List[MemberResponse])
def list_workspace_members(
    workspace_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all members of a workspace"""
    workspace = crud_workspace.get_by_id(db, workspace_id=workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Check if user is a member
    if not crud_workspace.is_member(db, workspace_id=workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )

    members = crud_workspace.get_members(db, workspace_id=workspace_id)

    # Enrich with user details
    result = []
    for member in members:
        user = crud_user.get_by_id(db, user_id=member.user_id)
        result.append(MemberResponse(
            id=member.id,
            workspace_id=member.workspace_id,
            user_id=member.user_id,
            role=member.role.value,
            joined_at=member.joined_at,
            user_name=user.name if user else None,
            user_email=user.email if user else None
        ))

    return result


@router.patch("/{workspace_id}/members/{user_id}", response_model=MemberResponse)
def update_member_role(
    workspace_id: UUID,
    user_id: UUID,
    role_update: MemberUpdateRole,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a member's role (owner only)"""
    workspace = crud_workspace.get_by_id(db, workspace_id=workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Check if current user is the owner
    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can update member roles"
        )

    # Get the member to update
    member = crud_workspace.get_member(db, workspace_id=workspace_id, user_id=user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    # Prevent owner from changing their own role
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )

    # Update role
    try:
        new_role = WorkspaceRole(role_update.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be: owner, editor, or viewer"
        )

    updated_member = crud_workspace.update_member_role(db, member=member, new_role=new_role)

    # Get user details
    user = crud_user.get_by_id(db, user_id=updated_member.user_id)

    return MemberResponse(
        id=updated_member.id,
        workspace_id=updated_member.workspace_id,
        user_id=updated_member.user_id,
        role=updated_member.role.value,
        joined_at=updated_member.joined_at,
        user_name=user.name if user else None,
        user_email=user.email if user else None
    )


@router.delete("/{workspace_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    workspace_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove a member from workspace (owner only)"""
    workspace = crud_workspace.get_by_id(db, workspace_id=workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Check if current user is the owner
    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can remove members"
        )

    # Prevent owner from removing themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove yourself from the workspace"
        )

    # Get the member to remove
    member = crud_workspace.get_member(db, workspace_id=workspace_id, user_id=user_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    crud_workspace.remove_member(db, member=member)
    return None


# Invitation Management Endpoints (must come BEFORE generic /{workspace_id} routes)

@router.post("/{workspace_id}/invitations", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
def invite_member(
    workspace_id: UUID,
    invitation_in: InvitationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Invite a new member to workspace (owner only)"""
    workspace = crud_workspace.get_by_id(db, workspace_id=workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Check if current user is the owner
    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can invite members"
        )

    # Check if user is already a member
    existing_user = crud_user.get_by_email(db, email=invitation_in.email)
    if existing_user:
        is_already_member = crud_workspace.is_member(db, workspace_id=workspace_id, user_id=existing_user.id)
        if is_already_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this workspace"
            )

    # Check if there's already a pending invitation
    existing_invitation = crud_invitation.get_pending_by_email(
        db, email=invitation_in.email, workspace_id=workspace_id
    )
    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation already sent to this email"
        )

    # Validate role
    try:
        WorkspaceRole(invitation_in.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be: owner, editor, or viewer"
        )

    # Create invitation
    invitation = crud_invitation.create(
        db,
        workspace_id=workspace_id,
        inviter_id=current_user.id,
        invitation_in=invitation_in
    )

    # Send invitation email
    email_service.send_invitation_email(
        recipient_email=invitation_in.email,
        workspace_name=workspace.name,
        inviter_name=current_user.name,
        invitation_token=invitation.token,
        role=invitation_in.role
    )

    return invitation


@router.get("/{workspace_id}/invitations", response_model=List[InvitationResponse])
def list_invitations(
    workspace_id: UUID,
    status_filter: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all invitations for a workspace (owner only)"""
    workspace = crud_workspace.get_by_id(db, workspace_id=workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Check if current user is the owner
    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can view invitations"
        )

    invitations = crud_invitation.get_by_workspace(db, workspace_id=workspace_id, status=status_filter)
    return invitations


@router.delete("/{workspace_id}/invitations/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_invitation(
    workspace_id: UUID,
    invitation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Revoke an invitation (owner only)"""
    workspace = crud_workspace.get_by_id(db, workspace_id=workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Check if current user is the owner
    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can revoke invitations"
        )

    invitation = crud_invitation.get_by_id(db, invitation_id=invitation_id)
    if not invitation or invitation.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )

    crud_invitation.revoke_invitation(db, invitation=invitation)
    return None


# Generic Workspace CRUD Endpoints (must come AFTER specific routes)

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get workspace details"""
    workspace = crud_workspace.get_by_id(db, workspace_id=workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Check if user is a member
    if not crud_workspace.is_member(db, workspace_id=workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )

    return workspace


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace(
    workspace_id: UUID,
    workspace_in: WorkspaceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update workspace"""
    workspace = crud_workspace.get_by_id(db, workspace_id=workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Check if user is a member
    if not crud_workspace.is_member(db, workspace_id=workspace_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this workspace"
        )

    updated_workspace = crud_workspace.update(db, workspace=workspace, workspace_in=workspace_in)
    return updated_workspace


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete workspace (owner only)"""
    workspace = crud_workspace.get_by_id(db, workspace_id=workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )

    # Check if user is the owner
    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can delete the workspace"
        )

    crud_workspace.delete(db, workspace=workspace)
    return None
