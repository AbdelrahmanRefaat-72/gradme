"""
ExpectedEmailRule entity ORM model.
Stores user rules for monitoring expected emails in Inbox or Spam.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.database.base import Base, TimestampMixin


class RuleType(str, enum.Enum):
    SENDER_EMAIL = "SENDER_EMAIL"
    SENDER_DOMAIN = "SENDER_DOMAIN"
    SUBJECT_KEYWORD = "SUBJECT_KEYWORD"


class ExpectedEmailRule(Base, TimestampMixin):
    __tablename__ = "expected_email_rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    rule_type = Column(SQLEnum(RuleType), nullable=False)
    rule_value = Column(String, nullable=False)  # e.g., "hr@company.com", "amazon.com", "Interview"
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="expected_rules")
    matched_emails = relationship("Email", back_populates="matched_rule")
