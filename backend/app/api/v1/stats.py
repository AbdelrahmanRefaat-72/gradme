"""
Dashboard Metrics & Analytics API Router (v1).
Provides aggregated counters and security breakdown statistics for the frontend dashboard.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.email import Email
from app.models.suspicious_email import SuspiciousEmail, RiskLevel
from app.models.expected_rule import ExpectedEmailRule
from app.models.notification import Notification
from app.auth.security import get_current_user

router = APIRouter(prefix="/stats", tags=["Dashboard Metrics"])


@router.get("/dashboard")
def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns high-level security metrics and counters for the dashboard overview page.
    """
    user_id = current_user.id

    # 1. Email Counters
    total_emails = db.query(Email).filter(Email.user_id == user_id).count()
    suspicious_count = db.query(Email).filter(
        Email.user_id == user_id, 
        Email.is_suspicious == True
    ).count()
    expected_count = db.query(Email).filter(
        Email.user_id == user_id, 
        Email.is_expected == True
    ).count()

    # 2. Risk Level Breakdown
    high_risk_count = db.query(SuspiciousEmail).join(Email).filter(
        Email.user_id == user_id,
        SuspiciousEmail.risk_level == RiskLevel.HIGH_RISK
    ).count()
    
    medium_risk_count = db.query(SuspiciousEmail).join(Email).filter(
        Email.user_id == user_id,
        SuspiciousEmail.risk_level == RiskLevel.MEDIUM_RISK
    ).count()

    # 3. Rules & Notifications Counters
    active_rules_count = db.query(ExpectedEmailRule).filter(
        ExpectedEmailRule.user_id == user_id,
        ExpectedEmailRule.is_active == True
    ).count()

    unread_notifications = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).count()

    return {
        "total_emails": total_emails,
        "suspicious_count": suspicious_count,
        "expected_count": expected_count,
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
        "safe_count": total_emails - suspicious_count,
        "active_rules_count": active_rules_count,
        "unread_notifications": unread_notifications,
        "user_profile": {
            "email": current_user.email,
            "full_name": current_user.full_name,
            "telegram_connected": bool(current_user.telegram_chat_id),
        }
    }
