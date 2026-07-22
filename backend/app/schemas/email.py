"""
Email Pydantic DTO schemas.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.email import EmailFolder
from app.schemas.suspicious_email import SuspiciousEmailRead
from app.schemas.ai_summary import AISummaryRead


class EmailRead(BaseModel):
    id: int
    user_id: int
    gmail_message_id: str
    gmail_thread_id: Optional[str] = None
    sender: str
    reply_to: Optional[str] = None
    subject: Optional[str] = None
    snippet: Optional[str] = None
    received_date: datetime
    folder: EmailFolder
    is_suspicious: bool
    is_expected: bool
    matched_rule_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmailDetail(EmailRead):
    body_text: Optional[str] = None
    auth_headers_raw: Optional[str] = None
    suspicious_analysis: Optional[SuspiciousEmailRead] = None
    ai_summary: Optional[AISummaryRead] = None

    model_config = ConfigDict(from_attributes=True)
