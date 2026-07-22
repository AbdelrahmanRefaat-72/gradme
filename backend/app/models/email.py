"""
Email entity ORM model.
Stores fetched metadata and headers for incoming emails (from Inbox and Spam).
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.database.base import Base, TimestampMixin


class EmailFolder(str, enum.Enum):
    INBOX = "INBOX"
    SPAM = "SPAM"
    TRASH = "TRASH"


class Email(Base, TimestampMixin):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    gmail_message_id = Column(String, unique=True, index=True, nullable=False)
    gmail_thread_id = Column(String, index=True, nullable=True)

    sender = Column(String, nullable=False, index=True)
    reply_to = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    snippet = Column(Text, nullable=True)
    body_text = Column(Text, nullable=True)
    received_date = Column(DateTime, nullable=False)

    folder = Column(SQLEnum(EmailFolder), default=EmailFolder.INBOX, nullable=False)
    auth_headers_raw = Column(Text, nullable=True)  # Raw Authentication-Results / Received headers
    
    is_suspicious = Column(Boolean, default=False, nullable=False, index=True)
    is_expected = Column(Boolean, default=False, nullable=False, index=True)
    matched_rule_id = Column(Integer, ForeignKey("expected_email_rules.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="emails")
    matched_rule = relationship("ExpectedEmailRule", back_populates="matched_emails")
    suspicious_analysis = relationship("SuspiciousEmail", back_populates="email", uselist=False, cascade="all, delete-orphan")
    ai_summary = relationship("AISummary", back_populates="email", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="email", cascade="all, delete-orphan")
