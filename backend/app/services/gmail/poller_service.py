"""
Continuous Background Email Polling Worker.
Periodically fetches new emails for all registered users, triggers threat analysis,
and dispatches Telegram notifications.
"""

import asyncio
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.user import User
from app.models.oauth_token import OAuthToken
from app.services.gmail.gmail_service import GmailService
from app.services.gmail.expected_service import ExpectedEmailService
from app.services.notifications.telegram_service import TelegramNotificationService


class EmailPollerWorker:
    """
    Background worker for continuous email security monitoring.
    """

    @classmethod
    async def poll_all_users_once(cls):
        """
        Executes one polling iteration across all registered active users.
        """
        db: Session = SessionLocal()
        try:
            # Query users with OAuth tokens
            users = db.query(User).join(OAuthToken).filter(User.is_active == True).all()

            for user in users:
                try:
                    # 1. Fetch INBOX & SPAM emails and run Phishing Engine
                    fetched_emails = GmailService.fetch_user_emails(user.id, db, max_results=10)

                    # Send high-risk phishing warnings to Telegram immediately
                    for email in fetched_emails:
                        if email.is_suspicious and email.suspicious_analysis:
                            if email.suspicious_analysis.risk_level.value == "HIGH_RISK":
                                # Check if notification already sent
                                existing_notif = [n for n in email.notifications if n.notification_type.value == "PHISHING_ALERT"]
                                if not existing_notif:
                                    await TelegramNotificationService.notify_phishing_alert(
                                        user_chat_id=user.telegram_chat_id,
                                        user_id=user.id,
                                        email=email,
                                        suspicious_info=email.suspicious_analysis,
                                        db=db
                                    )

                    # 2. Evaluate Expected Email Rules & send notifications
                    await ExpectedEmailService.evaluate_expected_rules_for_user(user.id, db)

                except Exception as user_err:
                    print(f"[EmailPollerWorker] Error processing user_id={user.id}: {str(user_err)}")
        finally:
            db.close()

    @classmethod
    async def start_polling_loop(cls, poll_interval_seconds: int = 60):
        """
        Asynchronous infinite loop for background email synchronization.
        """
        print(f"[EmailPollerWorker] Background Gmail poller started (Interval: {poll_interval_seconds}s)...")
        while True:
            try:
                await cls.poll_all_users_once()
            except Exception as err:
                print(f"[EmailPollerWorker] Error in background polling loop: {str(err)}")
            
            await asyncio.sleep(poll_interval_seconds)
