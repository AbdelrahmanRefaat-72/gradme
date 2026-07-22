"""
Export all SQLAlchemy models for metadata initialization.
"""

from app.database.base import Base
from app.models.user import User
from app.models.oauth_token import OAuthToken
from app.models.expected_rule import ExpectedEmailRule, RuleType
from app.models.email import Email, EmailFolder
from app.models.suspicious_email import SuspiciousEmail, RiskLevel
from app.models.ai_summary import AISummary
from app.models.notification import Notification, NotificationType

__all__ = [
    "Base",
    "User",
    "OAuthToken",
    "ExpectedEmailRule",
    "RuleType",
    "Email",
    "EmailFolder",
    "SuspiciousEmail",
    "RiskLevel",
    "AISummary",
    "Notification",
    "NotificationType",
]
