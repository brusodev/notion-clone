from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
import secrets
from app.models.invitation import Invitation, InvitationStatus
from app.models.workspace_member import WorkspaceMember, WorkspaceRole
from app.schemas.invitation import InvitationCreate


def generate_invitation_token() -> str:
    """Generate a secure random token for invitations"""
    return secrets.token_urlsafe(32)


def create(
    db: Session,
    workspace_id: UUID,
    inviter_id: UUID,
    invitation_in: InvitationCreate,
    expires_in_days: int = 7
) -> Invitation:
    """Create a new workspace invitation"""
    invitation = Invitation(
        workspace_id=workspace_id,
        inviter_id=inviter_id,
        invitee_email=invitation_in.email.lower(),
        role=WorkspaceRole(invitation_in.role),
        token=generate_invitation_token(),
        status=InvitationStatus.PENDING,
        expires_at=datetime.utcnow() + timedelta(days=expires_in_days)
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation


def get_by_token(db: Session, token: str) -> Optional[Invitation]:
    """Get invitation by token"""
    return db.query(Invitation).filter(Invitation.token == token).first()


def get_by_id(db: Session, invitation_id: UUID) -> Optional[Invitation]:
    """Get invitation by ID"""
    return db.query(Invitation).filter(Invitation.id == invitation_id).first()


def get_by_workspace(
    db: Session,
    workspace_id: UUID,
    status: Optional[str] = None
) -> List[Invitation]:
    """Get all invitations for a workspace, optionally filtered by status"""
    query = db.query(Invitation).filter(Invitation.workspace_id == workspace_id)
    if status:
        query = query.filter(Invitation.status == status)
    return query.order_by(Invitation.created_at.desc()).all()


def get_pending_by_email(db: Session, email: str, workspace_id: UUID) -> Optional[Invitation]:
    """Get pending invitation for a specific email and workspace"""
    return db.query(Invitation).filter(
        Invitation.invitee_email == email.lower(),
        Invitation.workspace_id == workspace_id,
        Invitation.status == InvitationStatus.PENDING
    ).first()


def accept_invitation(
    db: Session,
    invitation: Invitation,
    user_id: UUID
) -> WorkspaceMember:
    """Accept an invitation and create workspace membership"""
    # Update invitation status
    invitation.status = InvitationStatus.ACCEPTED
    invitation.accepted_at = datetime.utcnow()

    # Create workspace membership
    member = WorkspaceMember(
        workspace_id=invitation.workspace_id,
        user_id=user_id,
        role=invitation.role
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def revoke_invitation(db: Session, invitation: Invitation) -> Invitation:
    """Revoke an invitation"""
    invitation.status = InvitationStatus.REVOKED
    db.commit()
    db.refresh(invitation)
    return invitation


def is_valid(invitation: Invitation) -> bool:
    """Check if invitation is valid (pending and not expired)"""
    if invitation.status != InvitationStatus.PENDING:
        return False
    if invitation.expires_at < datetime.utcnow():
        return False
    return True


def mark_expired_invitations(db: Session) -> int:
    """Mark all expired invitations as expired (utility function)"""
    expired_count = db.query(Invitation).filter(
        Invitation.status == InvitationStatus.PENDING,
        Invitation.expires_at < datetime.utcnow()
    ).update({Invitation.status: InvitationStatus.EXPIRED})
    db.commit()
    return expired_count
