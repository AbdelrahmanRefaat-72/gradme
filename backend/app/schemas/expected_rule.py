"""
ExpectedEmailRule Pydantic DTO schemas.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from app.models.expected_rule import RuleType


class ExpectedRuleCreate(BaseModel):
    rule_type: RuleType
    rule_value: str = Field(..., min_length=1, description="Target email, domain, or subject keyword")
    description: Optional[str] = None


class ExpectedRuleRead(BaseModel):
    id: int
    user_id: int
    rule_type: RuleType
    rule_value: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
