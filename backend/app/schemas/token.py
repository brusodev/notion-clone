from pydantic import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.user import UserResponse


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(Token):
    user: "UserResponse"


# Rebuild model after all imports are complete
def setup_models():
    """Setup forward references after all schemas are imported"""
    from app.schemas.user import UserResponse
    AuthResponse.model_rebuild()


class TokenPayload(BaseModel):
    sub: str  # user_id
    email: str
    exp: int
    type: str  # 'access' or 'refresh'


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
