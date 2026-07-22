"""
SuspiciousEmail entity ORM model.
Stores detailed analysis results produced by the Rule-Based Phishing Detection Engine.
"""

from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.database.base import Base, TimestampMixin


class RiskLevel(str, enum.Enum):
    SAFE = "SAFE"
    MEDIUM_RISK = "MEDIUM_RISK"
    HIGH_RISK = "HIGH_RISK"


class SuspiciousEmail(Base, TimestampMixin):
    __tablename__ = "suspicious_emails"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id", ondelete="CASCADE"), unique=True, nullable=False)

    risk_score = Column(Integer, nullable=False, index=True)  # 0 to 100+
    risk_level = Column(SQLEnum(RiskLevel), nullable=False, index=True)
    reasons = Column(JSON, nullable=False)  # Array of string reasons (e.g. ["SPF Failed", "Reply-To Mismatch"])
    recommendation = Column(Text, nullable=False)

    # Relationships
    email = relationship("Email", back_populates="suspicious_analysis")
