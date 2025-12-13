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


class TokenPayload(BaseModel):
    sub: str  # user_id
    email: str
    exp: int
    type: str  # 'access' or 'refresh'


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
