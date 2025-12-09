from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class InvitationCreate(BaseModel):
    """Schema for creating a new invitation"""
    email: EmailStr = Field(..., description="Email address of the person to invite")
    role: str = Field("viewer", description="Role to assign (owner, editor, viewer)")


class InvitationAccept(BaseModel):
    """Schema for accepting an invitation"""
    token: str = Field(..., description="Invitation token from email")


class InvitationResponse(BaseModel):
    """Schema for invitation response"""
    id: UUID
    workspace_id: UUID
    inviter_id: UUID
    invitee_email: str
    role: str
    status: str
    token: str  # Added for testing/development - allows accepting invitation
    expires_at: datetime
    created_at: datetime
    accepted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class InvitationWithDetails(InvitationResponse):
    """Extended invitation response with workspace and inviter details"""
    workspace_name: Optional[str] = None
    inviter_name: Optional[str] = None
    inviter_email: Optional[str] = None


class MemberUpdateRole(BaseModel):
    """Schema for updating member role"""
    role: str = Field(..., description="New role (owner, editor, viewer)")


class MemberResponse(BaseModel):
    """Schema for workspace member with user details"""
    id: UUID
    workspace_id: UUID
    user_id: UUID
    role: str
    joined_at: datetime
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
