import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)


class UserCreate(UserBase):
    """Used for email/password registration."""
    password: str = Field(min_length=8, max_length=128)


class UserPublic(UserBase):
    """Safe user data returned to clients — never exposes password_hash."""
    id: uuid.UUID
    avatar_url: str | None
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    avatar_url: str | None = None
