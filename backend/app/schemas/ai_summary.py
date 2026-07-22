"""
AISummary Pydantic DTO schemas.
"""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class AISummaryRead(BaseModel):
    id: int
    email_id: int
    summary_headline: str
    bullet_points: List[str]
    extracted_dates: Optional[List[str]] = []
    extracted_times: Optional[List[str]] = []
    extracted_deadlines: Optional[List[str]] = []
    extracted_locations: Optional[List[str]] = []
    action_items: Optional[List[str]] = []
    important_names: Optional[List[str]] = []
    important_links: Optional[List[str]] = []

    model_config = ConfigDict(from_attributes=True)
