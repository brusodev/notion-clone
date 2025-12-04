from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember, WorkspaceRole
from app.models.user import User
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


def create(db: Session, workspace_in: WorkspaceCreate, owner_id: UUID) -> Workspace:
    """Create a new workspace and add owner as member"""
    workspace = Workspace(
        name=workspace_in.name,
        icon=workspace_in.icon,
        owner_id=owner_id
    )
    db.add(workspace)
    db.flush()
    
    # Add owner as workspace member
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=owner_id,
        role=WorkspaceRole.OWNER
    )
    db.add(member)
    db.commit()
    db.refresh(workspace)
    return workspace


def get_by_id(db: Session, workspace_id: UUID) -> Optional[Workspace]:
    """Get workspace by ID"""
    return db.query(Workspace).filter(Workspace.id == workspace_id).first()


def get_by_user(db: Session, user_id: UUID) -> List[Workspace]:
    """Get all workspaces where user is a member"""
    return db.query(Workspace).join(WorkspaceMember).filter(
        WorkspaceMember.user_id == user_id
    ).all()


def update(db: Session, workspace: Workspace, workspace_in: WorkspaceUpdate) -> Workspace:
    """Update workspace"""
    update_data = workspace_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workspace, field, value)
    db.commit()
    db.refresh(workspace)
    return workspace


def delete(db: Session, workspace: Workspace) -> None:
    """Delete workspace"""
    db.delete(workspace)
    db.commit()


def is_member(db: Session, workspace_id: UUID, user_id: UUID) -> bool:
    """Check if user is a member of workspace"""
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id
    ).first()
    return member is not None


def get_user_role(db: Session, workspace_id: UUID, user_id: UUID) -> Optional[WorkspaceRole]:
    """Get user's role in workspace"""
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id
    ).first()
    return member.role if member else None


# Member Management Functions

def get_members(db: Session, workspace_id: UUID) -> List[WorkspaceMember]:
    """Get all members of a workspace"""
    return db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id
    ).all()


def get_member(db: Session, workspace_id: UUID, user_id: UUID) -> Optional[WorkspaceMember]:
    """Get a specific workspace member"""
    return db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id
    ).first()


def update_member_role(
    db: Session,
    member: WorkspaceMember,
    new_role: WorkspaceRole
) -> WorkspaceMember:
    """Update a member's role in workspace"""
    member.role = new_role
    db.commit()
    db.refresh(member)
    return member


def remove_member(db: Session, member: WorkspaceMember) -> None:
    """Remove a member from workspace"""
    db.delete(member)
    db.commit()
