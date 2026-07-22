"""
AI Summary Service Orchestrator.
Manages provider resolution and persists AISummary entities into database.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.config.config import settings
from app.models.email import Email
from app.models.ai_summary import AISummary
from app.services.ai.base_provider import LLMProvider
from app.services.ai.gemini_provider import GeminiProvider


class AISummaryService:
    """
    Service for generating and storing AI Summaries for emails.
    """

    def __init__(self, provider: Optional[LLMProvider] = None):
        if provider:
            self.provider = provider
        else:
            # Default to GeminiProvider; easy to swap with OpenAIProvider in the future
            self.provider = GeminiProvider()

    async def generate_and_save_summary(self, email: Email, db: Session) -> AISummary:
        """
        Generates AI summary for an email and saves it in the database.
        If summary already exists, returns existing record.
        """
        existing = db.query(AISummary).filter(AISummary.email_id == email.id).first()
        if existing:
            return existing

        content = email.body_text or email.snippet or ""
        summary_dict = await self.provider.summarize_email(
            subject=email.subject or "",
            sender=email.sender,
            content=content
        )

        ai_summary_record = AISummary(
            email_id=email.id,
            summary_headline=summary_dict["summary_headline"],
            bullet_points=summary_dict["bullet_points"],
            extracted_dates=summary_dict.get("extracted_dates"),
            extracted_times=summary_dict.get("extracted_times"),
            extracted_deadlines=summary_dict.get("extracted_deadlines"),
            extracted_locations=summary_dict.get("extracted_locations"),
            action_items=summary_dict.get("action_items"),
            important_names=summary_dict.get("important_names"),
            important_links=summary_dict.get("important_links"),
        )
        db.add(ai_summary_record)
        db.commit()
        db.refresh(ai_summary_record)

        return ai_summary_record
