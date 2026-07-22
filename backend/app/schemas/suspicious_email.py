"""
SuspiciousEmail Pydantic DTO schemas.
"""

from pydantic import BaseModel, ConfigDict
from typing import List
from app.models.suspicious_email import RiskLevel


class SuspiciousEmailRead(BaseModel):
    id: int
    email_id: int
    risk_score: int
    risk_level: RiskLevel
    reasons: List[str]
    recommendation: str

    model_config = ConfigDict(from_attributes=True)
