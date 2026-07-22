"""
User Pydantic DTO schemas.
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    picture_url: Optional[str] = None


class UserRead(UserBase):
    id: int
    google_id: str
    telegram_chat_id: Optional[str] = None
    is_active: bool
    last_login_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserTelegramUpdate(BaseModel):
    telegram_chat_id: str
