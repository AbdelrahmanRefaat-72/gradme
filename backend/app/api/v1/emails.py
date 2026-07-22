"""
Email Management API Router (v1).
Endpoints for listing recent emails, suspicious emails, expected emails, and syncing Gmail.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.email import Email, EmailFolder
from app.schemas.email import EmailRead, EmailDetail
from app.auth.security import get_current_user
from app.services.gmail.gmail_service import GmailService
from app.services.gmail.auth_service import GmailAuthorizationError
from app.services.gmail.expected_service import ExpectedEmailService

router = APIRouter(prefix="/emails", tags=["Emails"])


@router.get("/recent", response_model=List[EmailRead])
def get_recent_emails(
    limit: int = Query(20, ge=1, le=100),
    folder: Optional[EmailFolder] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns recent emails fetched for the current user.
    Supports optional filtering by folder (INBOX / SPAM).
    """
    query = db.query(Email).filter(Email.user_id == current_user.id)
    if folder:
        query = query.filter(Email.folder == folder)
    
    emails = query.order_by(Email.received_date.desc()).limit(limit).all()
    return emails


@router.get("/suspicious", response_model=List[EmailDetail])
def get_suspicious_emails(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns emails flagged as suspicious by the Rule-Based Phishing Engine.
    """
    emails = db.query(Email).filter(
        Email.user_id == current_user.id,
        Email.is_suspicious == True
    ).order_by(Email.received_date.desc()).limit(limit).all()
    return emails


@router.get("/expected", response_model=List[EmailDetail])
def get_expected_emails(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns emails matched by user-defined Expected Email Rules.
    """
    emails = db.query(Email).filter(
        Email.user_id == current_user.id,
        Email.is_expected == True
    ).order_by(Email.received_date.desc()).limit(limit).all()
    return emails


@router.get("/{email_id}", response_model=EmailDetail)
def get_email_by_id(
    email_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns complete detail for a specific email including threat analysis & AI summary.
    """
    email = db.query(Email).filter(
        Email.id == email_id,
        Email.user_id == current_user.id
    ).first()

    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found."
        )

    return email


@router.post("/sync")
async def sync_user_emails(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Triggers an immediate Gmail sync for the current user.
    Fetches INBOX and SPAM, runs Phishing Engine, and checks Expected Email Rules.
    """
    try:
        fetched_emails = GmailService.fetch_user_emails(current_user.id, db, max_results=15)
        matched_expected = await ExpectedEmailService.evaluate_expected_rules_for_user(current_user.id, db)
        
        return {
            "message": "Gmail synchronization completed successfully.",
            "total_fetched": len(fetched_emails),
            "expected_matched": len(matched_expected),
        }
    except GmailAuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email synchronization failed: {str(e)}"
        )
