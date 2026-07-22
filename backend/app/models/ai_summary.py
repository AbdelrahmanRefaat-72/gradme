"""
AISummary entity ORM model.
Stores structured AI-generated summaries for important and expected emails.
"""

from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin


class AISummary(Base, TimestampMixin):
    __tablename__ = "ai_summaries"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id", ondelete="CASCADE"), unique=True, nullable=False)

    summary_headline = Column(String, nullable=False)
    bullet_points = Column(JSON, nullable=False)  # List[str]
    extracted_dates = Column(JSON, nullable=True)  # List[str]
    extracted_times = Column(JSON, nullable=True)  # List[str]
    extracted_deadlines = Column(JSON, nullable=True)  # List[str]
    extracted_locations = Column(JSON, nullable=True)  # List[str]
    action_items = Column(JSON, nullable=True)  # List[str]
    important_names = Column(JSON, nullable=True)  # List[str]
    important_links = Column(JSON, nullable=True)  # List[str]

    # Relationships
    email = relationship("Email", back_populates="ai_summary")
