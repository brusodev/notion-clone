from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.crud import invitation as crud_invitation
from app.schemas.invitation import InvitationAccept
from app.models.user import User

router = APIRouter()


@router.post("/accept", status_code=status.HTTP_200_OK)
def accept_invitation(
    accept_data: InvitationAccept,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Accept a workspace invitation using the invitation token"""
    # Get invitation by token
    invitation = crud_invitation.get_by_token(db, token=accept_data.token)
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )

    # Check if invitation is valid
    if not crud_invitation.is_valid(invitation):
        if invitation.status == "accepted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation has already been accepted"
            )
        elif invitation.status == "revoked":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation has been revoked"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation has expired"
            )

    # Check if invitation email matches current user
    if invitation.invitee_email.lower() != current_user.email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invitation was sent to a different email address"
        )

    # Accept invitation and create membership
    try:
        member = crud_invitation.accept_invitation(db, invitation=invitation, user_id=current_user.id)
    except Exception as e:
        # Check if user is already a member
        if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already a member of this workspace"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept invitation"
        )

    return {
        "message": "Invitation accepted successfully",
        "workspace_id": str(member.workspace_id),
        "role": member.role.value
    }
