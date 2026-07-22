"""
Notification entity ORM model.
Stores dispatch logs and read states for Telegram alerts and dashboard notifications.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.database.base import Base, TimestampMixin


class NotificationType(str, enum.Enum):
    EXPECTED_EMAIL = "EXPECTED_EMAIL"
    PHISHING_ALERT = "PHISHING_ALERT"
    SYSTEM_NOTICE = "SYSTEM_NOTICE"


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    email_id = Column(Integer, ForeignKey("emails.id", ondelete="CASCADE"), nullable=True, index=True)

    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String, nullable=False)
    message_text = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    
    sent_to_telegram = Column(Boolean, default=False, nullable=False)
    telegram_status = Column(String, nullable=True)  # e.g., "DELIVERED", "FAILED", "DISABLED"

    # Relationships
    email = relationship("Email", back_populates="notifications")
