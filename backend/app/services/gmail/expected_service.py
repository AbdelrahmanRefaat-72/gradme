"""
Expected Email Matching & Processing Service.
Evaluates user rules against incoming emails in INBOX and SPAM, triggers AI summarization,
and dispatches Telegram alerts.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.email import Email
from app.models.expected_rule import ExpectedEmailRule, RuleType
from app.utils.header_parser import extract_email_and_domain
from app.services.ai.summary_service import AISummaryService
from app.services.notifications.telegram_service import TelegramNotificationService


class ExpectedEmailService:
    """
    Service for checking expected email rules and triggering AI summaries & notifications.
    """

    @classmethod
    async def evaluate_expected_rules_for_user(cls, user_id: int, db: Session) -> List[Email]:
        """
        Evaluates active ExpectedEmailRules for a user against all unprocessed emails.
        Returns list of newly matched expected emails.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        active_rules = db.query(ExpectedEmailRule).filter(
            ExpectedEmailRule.user_id == user_id,
            ExpectedEmailRule.is_active == True
        ).all()

        if not active_rules:
            return []

        # Query emails for user that have not yet been evaluated for expected rules
        unprocessed_emails = db.query(Email).filter(
            Email.user_id == user_id,
            Email.is_expected == False
        ).all()

        matched_emails: List[Email] = []
        ai_service = AISummaryService()

        for email in unprocessed_emails:
            matching_rule = cls._match_email_against_rules(email, active_rules)
            if matching_rule:
                # Mark as expected email
                email.is_expected = True
                email.matched_rule_id = matching_rule.id
                db.commit()

                # Generate AI Summary
                ai_summary = await ai_service.generate_and_save_summary(email, db)

                # Send Telegram Notification
                await TelegramNotificationService.notify_expected_email(
                    user_chat_id=user.telegram_chat_id,
                    user_id=user.id,
                    email=email,
                    ai_summary=ai_summary,
                    db=db
                )

                matched_emails.append(email)

        return matched_emails

    @classmethod
    def _match_email_against_rules(
        cls, 
        email: Email, 
        rules: List[ExpectedEmailRule]
    ) -> Optional[ExpectedEmailRule]:
        """
        Checks if an email matches any active ExpectedEmailRule.
        """
        sender_email, sender_domain = extract_email_and_domain(email.sender)
        subject_lower = (email.subject or "").lower()

        for rule in rules:
            val_lower = rule.rule_value.strip().lower()

            if rule.rule_type == RuleType.SENDER_EMAIL:
                if sender_email and sender_email == val_lower:
                    return rule

            elif rule.rule_type == RuleType.SENDER_DOMAIN:
                if sender_domain and sender_domain == val_lower:
                    return rule

            elif rule.rule_type == RuleType.SUBJECT_KEYWORD:
                if val_lower in subject_lower:
                    return rule

        return None
