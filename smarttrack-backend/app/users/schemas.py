import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


Programme = Literal["General Science", "General Arts", "Business", "Visual Arts", "Home Economics", "Technical"]
SHSLevel = Literal["SHS 1", "SHS 2", "SHS 3", "Completed SHS"]


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)


class UserCreate(UserBase):
    """Used for email/password registration."""
    password: str = Field(min_length=8, max_length=128)


class UserPublic(UserBase):
    """Safe user data returned to clients — never exposes password_hash."""
    id: uuid.UUID
    avatar_url: str | None = None
    is_verified: bool
    created_at: datetime

    # SHS onboarding
    programme: str | None = None
    shs_level: str | None = None
    school: str | None = None
    onboarding_completed: bool = False
    starter_arena_completed: bool = False

    # Gamification
    xp: int = 0
    rank: str = "Beginner"
    streak: int = 0

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    avatar_url: str | None = None
    programme: Programme | None = None
    shs_level: SHSLevel | None = None
    school: str | None = Field(default=None, max_length=255)
    onboarding_completed: bool | None = None
    starter_arena_completed: bool | None = None
