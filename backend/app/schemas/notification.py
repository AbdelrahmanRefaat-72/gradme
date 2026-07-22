"""
Notification Pydantic DTO schemas.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.notification import NotificationType


class NotificationRead(BaseModel):
    id: int
    user_id: int
    email_id: Optional[int] = None
    notification_type: NotificationType
    title: str
    message_text: str
    is_read: bool
    sent_to_telegram: bool
    telegram_status: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
