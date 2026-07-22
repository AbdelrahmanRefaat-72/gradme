"""
Sender History & Behavioral Analytics Rule.
Evaluates whether a sender is newly seen for the specific user account.
"""

from typing import Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.services.rules.base_rule import BasePhishingRule
from app.models.email import Email
from app.utils.header_parser import extract_email_and_domain


class NewlySeenSenderRule(BasePhishingRule):
    rule_name = "Newly Seen Sender"
    weight = 15

    def evaluate(self, email_data: Dict[str, Any], db: Session) -> Tuple[int, Optional[str]]:
        user_id = email_data.get("user_id")
        sender_header = email_data.get("sender", "")
        sender_email, _ = extract_email_and_domain(sender_header)

        if not user_id or not sender_email:
            return 0, None

        # Check existing emails table for previous emails from this sender
        previous_count = db.query(Email).filter(
            Email.user_id == user_id,
            Email.sender.ilike(f"%{sender_email}%")
        ).count()

        # If count is 0, this sender is newly seen for this user
        if previous_count == 0:
            return self.weight, f"Newly Seen Sender (No prior email history recorded from '{sender_email}')"

        return 0, None
