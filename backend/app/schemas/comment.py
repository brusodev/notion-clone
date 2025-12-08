from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ============================================================================
# User Basic Schema (for embedded user data)
# ============================================================================

class UserBasic(BaseModel):
    """Basic user information for embedding in comments"""
    id: UUID
    name: str
    email: str
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Reaction Schemas
# ============================================================================

class ReactionCreate(BaseModel):
    """Schema for creating a reaction"""
    reaction_type: str = Field(..., min_length=1, max_length=50)

    @field_validator('reaction_type')
    @classmethod
    def validate_reaction_type(cls, v: str) -> str:
        """Validate reaction type against allowed list"""
        allowed_reactions = {
            'thumbs_up', 'heart', 'laugh', 'surprised',
            'sad', 'rocket', 'eyes', 'party', 'fire'
        }
        if v not in allowed_reactions:
            raise ValueError(f'Reaction type must be one of: {", ".join(allowed_reactions)}')
        return v


class ReactionResponse(BaseModel):
    """Schema for reaction response"""
    id: UUID
    comment_id: UUID
    user_id: UUID
    reaction_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReactionSummary(BaseModel):
    """Summary of reactions grouped by type"""
    reaction_type: str
    count: int
    user_reacted: bool  # Whether current user has this reaction


# ============================================================================
# Attachment Schemas
# ============================================================================

class AttachmentCreate(BaseModel):
    """Schema for creating an attachment"""
    file_name: str = Field(..., min_length=1, max_length=500)
    file_url: str = Field(..., min_length=1, max_length=1000)
    file_size: Optional[int] = None
    mime_type: Optional[str] = Field(None, max_length=100)
    order_index: int = Field(default=0)


class AttachmentResponse(BaseModel):
    """Schema for attachment response"""
    id: UUID
    comment_id: UUID
    file_name: str
    file_url: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    uploaded_by: UUID
    order_index: int
    created_at: datetime
    uploader: Optional[UserBasic] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Comment Schemas
# ============================================================================

class CommentCreate(BaseModel):
    """Schema for creating a comment"""
    page_id: Optional[UUID] = None
    block_id: Optional[UUID] = None
    parent_comment_id: Optional[UUID] = None
    content: str = Field(..., min_length=1, max_length=10000)

    @model_validator(mode='after')
    def validate_target(self):
        """Validate that exactly one of page_id or block_id is set"""
        page_set = self.page_id is not None
        block_set = self.block_id is not None

        if page_set == block_set:  # Both True or both False
            raise ValueError('Exactly one of page_id or block_id must be provided')

        return self


class CommentUpdate(BaseModel):
    """Schema for updating a comment (only content can be edited)"""
    content: str = Field(..., min_length=1, max_length=10000)


class CommentResponse(BaseModel):
    """Schema for comment response with embedded data"""
    id: UUID
    page_id: Optional[UUID] = None
    block_id: Optional[UUID] = None
    parent_comment_id: Optional[UUID] = None
    thread_depth: int
    content: str
    author_id: UUID
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    edited_at: Optional[datetime] = None

    # Embedded data
    author: Optional[UserBasic] = None
    deleted_by_user: Optional[UserBasic] = None
    reactions: List[ReactionSummary] = []
    mentioned_users: List[UserBasic] = []
    attachments: List[AttachmentResponse] = []
    replies_count: int = 0

    # Metadata
    matched_in: Optional[str] = None  # For search results: 'title' or 'content'

    model_config = ConfigDict(from_attributes=True)


class CommentWithReplies(CommentResponse):
    """Schema for comment with nested replies (recursive)"""
    replies: List["CommentWithReplies"] = []


class CommentListResponse(BaseModel):
    """Schema for paginated comment list"""
    comments: List[CommentResponse]
    total: int
    page: int = 1
    page_size: int = 20
    has_more: bool


# ============================================================================
# Mention Schemas
# ============================================================================

class MentionResponse(BaseModel):
    """Schema for mention response"""
    id: UUID
    comment_id: UUID
    mentioned_user_id: UUID
    created_at: datetime
    mentioned_user: Optional[UserBasic] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Forward Reference Resolution
# ============================================================================

# Rebuild model to resolve forward references for recursive schema
CommentWithReplies.model_rebuild()
