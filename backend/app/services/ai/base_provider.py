"""
Abstract Base Class for LLM Providers.
Applies Strategy Pattern to allow swapping Gemini, OpenAI, or local LLMs seamlessly.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class LLMProvider(ABC):
    """
    Abstract interface for AI Summarization Providers.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Identifier for the AI provider."""
        pass

    @abstractmethod
    async def summarize_email(self, subject: str, sender: str, content: str) -> Dict[str, Any]:
        """
        Extracts structured bullet points, dates, deadlines, locations, action items, names, and links.
        Returns dictionary matching AISummary model fields.
        """
        pass
