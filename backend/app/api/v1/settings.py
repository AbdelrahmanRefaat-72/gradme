"""
User Settings & Integrations API Router (v1).
Endpoints for configuring Telegram Bot chat ID and dispatching test alerts.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import UserTelegramUpdate, UserRead
from app.auth.security import get_current_user
from app.services.notifications.telegram_service import TelegramNotificationService

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.post("/telegram", response_model=UserRead)
async def update_telegram_settings(
    data: UserTelegramUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates the user's Telegram Chat ID for receiving real-time security alerts.
    Dispatches a test welcome message upon connection.
    """
    chat_id = data.telegram_chat_id.strip()
    current_user.telegram_chat_id = chat_id
    db.commit()
    db.refresh(current_user)

    # Test Telegram connection
    if chat_id:
        test_msg = (
            "🤖 *Smart Email Guardian Connected*\n\n"
            "Your Telegram account has been successfully linked! "
            "You will now receive real-time alerts for expected emails and phishing threats."
        )
        await TelegramNotificationService.send_message(chat_id, test_msg)

    return current_user


@router.post("/telegram/test")
async def test_telegram_alert(
    current_user: User = Depends(get_current_user)
):
    """
    Sends a test Telegram alert message to verify integration.
    """
    if not current_user.telegram_chat_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Telegram Chat ID configured for this user account."
        )

    test_msg = (
        "🧪 *Test Security Notification*\n\n"
        "This is a test notification from Smart Email Guardian. "
        "Your alert pipeline is functioning perfectly!"
    )
    success = await TelegramNotificationService.send_message(current_user.telegram_chat_id, test_msg)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to deliver message via Telegram Bot. Please check bot token and Chat ID."
        )

    return {"message": "Test notification dispatched successfully."}
