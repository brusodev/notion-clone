from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime
from uuid import UUID
from app.models.page_permission import PermissionLevel


class PagePermissionCreate(BaseModel):
    """Schema for granting a new permission"""
    user_id: UUID = Field(..., description="User to grant permission to")
    permission_level: PermissionLevel = Field(
        default=PermissionLevel.VIEW,
        description="Permission level to grant"
    )


class PagePermissionUpdate(BaseModel):
    """Schema for updating an existing permission"""
    permission_level: PermissionLevel = Field(..., description="New permission level")


class PagePermissionShareByEmail(BaseModel):
    """Schema for sharing a page with a user by email"""
    email: EmailStr = Field(..., description="Email of user to share with")
    permission_level: PermissionLevel = Field(
        default=PermissionLevel.VIEW,
        description="Permission level to grant"
    )


class UserInfo(BaseModel):
    """Minimal user information for permission responses"""
    id: UUID
    email: str
    name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PagePermissionResponse(BaseModel):
    """Response schema for a page permission"""
    id: UUID
    page_id: UUID
    user_id: UUID
    permission_level: PermissionLevel
    granted_by: UUID | None = None
    created_at: datetime
    updated_at: datetime
    user: UserInfo | None = None
    granter: UserInfo | None = None

    model_config = ConfigDict(from_attributes=True)


class PagePermissionListResponse(BaseModel):
    """Response schema for listing page permissions"""
    total: int
    permissions: list[PagePermissionResponse]


class SharedPageInfo(BaseModel):
    """Information about a page that has been shared with the user"""
    id: UUID
    page_id: UUID
    permission_level: PermissionLevel
    created_at: datetime
    page_title: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SharedPagesListResponse(BaseModel):
    """Response schema for listing pages shared with a user"""
    total: int
    shared_pages: list[SharedPageInfo]


class PermissionCheckResponse(BaseModel):
    """Response schema for permission checks"""
    has_permission: bool
    permission_level: PermissionLevel | None = None
    can_view: bool = False
    can_comment: bool = False
    can_edit: bool = False
