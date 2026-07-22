"""
Export all Pydantic DTO schemas.
"""

from app.schemas.user import UserRead, UserTelegramUpdate
from app.schemas.expected_rule import ExpectedRuleCreate, ExpectedRuleRead
from app.schemas.email import EmailRead, EmailDetail
from app.schemas.suspicious_email import SuspiciousEmailRead
from app.schemas.ai_summary import AISummaryRead
from app.schemas.notification import NotificationRead

__all__ = [
    "UserRead",
    "UserTelegramUpdate",
    "ExpectedRuleCreate",
    "ExpectedRuleRead",
    "EmailRead",
    "EmailDetail",
    "SuspiciousEmailRead",
    "AISummaryRead",
    "NotificationRead",
]
