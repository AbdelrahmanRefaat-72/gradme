"""
Telegram Bot Notification Service.
Formats and dispatches real-time Telegram Markdown alerts for expected emails and phishing threats.
"""

import httpx
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.config.config import settings
from app.models.email import Email
from app.models.suspicious_email import SuspiciousEmail
from app.models.ai_summary import AISummary
from app.models.notification import Notification, NotificationType


class TelegramNotificationService:
    """
    Service for formatting and delivering Telegram bot notifications.
    """

    @staticmethod
    async def send_message(chat_id: str, text: str) -> bool:
        """
        Posts a Markdown formatted text message to a Telegram chat using Telegram Bot API.
        """
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token or bot_token == "your-telegram-bot-token" or not chat_id:
            print(f"[TelegramService] Telegram Bot unconfigured or invalid chat_id='{chat_id}'. Skipping dispatch.")
            return False

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"



        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }



        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    return True
                else:
                    print(f"[TelegramService] Telegram API error {response.status_code}: {response.text}")
                    return False
        except Exception as err:
            print(f"[TelegramService] Exception posting to Telegram: {str(err)}")
            return False

    @classmethod
    async def notify_expected_email(
        cls, 
        user_chat_id: Optional[str], 
        user_id: int, 
        email: Email, 
        ai_summary: Optional[AISummary], 
        db: Session
    ) -> Notification:
        """
        Formats and sends an Expected Email arrival alert to Telegram and logs in Notification table.
        """
        title = "Expected Email Arrived"
        
        # Build Markdown Message
        lines = [
            f"🎯 *Expected Email Arrived*",
            f"",
            f"*From:* {email.sender}",
            f"*Subject:* {email.subject or '(No Subject)'}",
        ]

        if ai_summary:
            lines.append(f"")
            lines.append(f"*Summary:*")
            lines.append(f"• {ai_summary.summary_headline}")
            for bp in ai_summary.bullet_points[:3]:
                lines.append(f"• {bp}")
            if ai_summary.extracted_dates:
                lines.append(f"• *Date:* {', '.join(ai_summary.extracted_dates)}")
            if ai_summary.extracted_times:
                lines.append(f"• *Time:* {', '.join(ai_summary.extracted_times)}")
            if ai_summary.extracted_locations:
                lines.append(f"• *Location:* {', '.join(ai_summary.extracted_locations)}")

        message_text = "\n".join(lines)

        # Dispatch via Telegram
        sent_success = False
        if user_chat_id:
            sent_success = await cls.send_message(user_chat_id, message_text)

        # Record in DB Notifications
        notification = Notification(
            user_id=user_id,
            email_id=email.id,
            notification_type=NotificationType.EXPECTED_EMAIL,
            title=title,
            message_text=message_text,
            is_read=False,
            sent_to_telegram=sent_success,
            telegram_status="DELIVERED" if sent_success else ("DISABLED" if not user_chat_id else "FAILED"),
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification

    @classmethod
    async def notify_phishing_alert(
        cls, 
        user_chat_id: Optional[str], 
        user_id: int, 
        email: Email, 
        suspicious_info: SuspiciousEmail, 
        db: Session
    ) -> Notification:
        """
        Formats and sends a Phishing Threat Warning alert to Telegram and logs in Notification table.
        """
        title = f"Phishing Threat Alert ({suspicious_info.risk_level.value})"
        
        reasons_formatted = "\n".join([f"• {r}" for r in suspicious_info.reasons])

        lines = [
            f"🚨 *Phishing Alert Warning*",
            f"",
            f"*Risk Score:* {suspicious_info.risk_score} ({suspicious_info.risk_level.value})",
            f"*From:* {email.sender}",
            f"*Subject:* {email.subject or '(No Subject)'}",
            f"",
            f"*Reasons:*",
            reasons_formatted,
            f"",
            f"*Recommendation:*",
            f"{suspicious_info.recommendation}"
        ]

        message_text = "\n".join(lines)

        # Dispatch via Telegram
        sent_success = False
        if user_chat_id:
            sent_success = await cls.send_message(user_chat_id, message_text)

        # Record in DB Notifications
        notification = Notification(
            user_id=user_id,
            email_id=email.id,
            notification_type=NotificationType.PHISHING_ALERT,
            title=title,
            message_text=message_text,
            is_read=False,
            sent_to_telegram=sent_success,
            telegram_status="DELIVERED" if sent_success else ("DISABLED" if not user_chat_id else "FAILED"),
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification


async def start_telegram_listener():
    """
    Background loop that polls Telegram for incoming /start messages.
    Automatically replies with the user's chat_id.
    """
    import asyncio
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token or bot_token == "your-telegram-bot-token" or not bot_token.strip():
        print("[TelegramListener] Telegram Bot Token is not configured. Listener disabled.")
        return

    print("[TelegramListener] Starting Telegram bot listener loop...")
    offset = 0
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    async with httpx.AsyncClient(timeout=10.0) as client:
        while True:
            try:
                response = await client.get(f"{url}?offset={offset}&timeout=5")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        for update in data.get("result", []):
                            update_id = update.get("update_id")
                            offset = update_id + 1
                            
                            message = update.get("message")
                            if not message:
                                continue
                            
                            chat = message.get("chat")
                            if not chat:
                                continue
                            
                            chat_id = chat.get("id")
                            text = message.get("text", "")
                            
                            if text.strip().startswith("/start"):
                                user_name = message.get("from", {}).get("first_name", "User")
                                welcome_text = (
                                    f"👋 *Hello {user_name}!*\n\n"
                                    f"I'm the *Smart Email Guardian* bot. I will deliver real-time security alerts directly to this chat.\n\n"
                                    f"🔑 *Your Telegram Chat ID:* `{chat_id}`\n\n"
                                    f"Please copy this ID and save it in the *Settings* tab of your Smart Email Guardian dashboard to complete the link!"
                                )
                                await client.post(send_url, json={
                                    "chat_id": chat_id,
                                    "text": welcome_text,
                                    "parse_mode": "Markdown"
                                })
                                print(f"[TelegramListener] Replied to /start from {user_name} (chat_id: {chat_id})")
            except Exception as err:
                print(f"[TelegramListener] Error in polling loop: {str(err)}")
            
            await asyncio.sleep(3)

