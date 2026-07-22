"""
AI Email Summaries API Router (v1).
Endpoints for fetching or generating AI email summaries.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.email import Email
from app.models.ai_summary import AISummary
from app.schemas.ai_summary import AISummaryRead
from app.auth.security import get_current_user
from app.services.ai.summary_service import AISummaryService

router = APIRouter(prefix="/summary", tags=["AI Summaries"])


@router.get("/{email_id}", response_model=AISummaryRead)
async def get_or_generate_email_summary(
    email_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the AI summary for a specific email.
    If a summary does not exist, generates it dynamically using the configured LLM.
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

    # Check if summary already exists
    existing = db.query(AISummary).filter(AISummary.email_id == email.id).first()
    if existing:
        return existing

    # Generate AI summary dynamically
    ai_service = AISummaryService()
    new_summary = await ai_service.generate_and_save_summary(email, db)

    return new_summary
