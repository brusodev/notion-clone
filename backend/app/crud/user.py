from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password


def create(db: Session, user_in: UserCreate) -> User:
    """Create a new user"""
    user = User(
        email=user_in.email,
        name=user_in.name,
        password_hash=hash_password(user_in.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def update(db: Session, user: User, user_in: UserUpdate) -> User:
    """Update user"""
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = get_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def is_active(user: User) -> bool:
    """Check if user is active"""
    return user.is_active
