"""
Abstract Base Class for Phishing Detection Rules.
Follows the Open-Closed Principle (SOLID) allowing new rules to be added without modifying core engine logic.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session


class BasePhishingRule(ABC):
    """
    Abstract base rule for evaluating specific threat indicators in an email.
    """

    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Human-readable identifier for the rule."""
        pass

    @property
    @abstractmethod
    def weight(self) -> int:
        """Risk score points contributed by this rule if triggered."""
        pass

    @abstractmethod
    def evaluate(self, email_data: Dict[str, Any], db: Session) -> Tuple[int, Optional[str]]:
        """
        Evaluates email metadata against the rule logic.
        Returns (score_points, reason_description_or_None).
        """
        pass
