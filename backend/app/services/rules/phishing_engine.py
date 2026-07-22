"""
Deterministic Rule-Based Phishing Engine Orchestrator.
Evaluates emails against security rules, computes total risk score, assigns risk tier, and generates recommendations.
"""

from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.suspicious_email import RiskLevel
from app.services.rules.base_rule import BasePhishingRule
from app.services.rules.auth_headers_rule import SPFFailureRule, DKIMFailureRule, DMARCFailureRule
from app.services.rules.domain_rules import ReplyToMismatchRule, DomainSimilarityRule, SuspiciousTLDRule
from app.services.rules.content_rules import SuspiciousKeywordsRule, URLShortenerRule
from app.services.rules.sender_history_rule import NewlySeenSenderRule


class PhishingEngineService:
    """
    Engine orchestrating rule-based threat evaluation.
    Guarantees transparent, zero-hallucination threat scoring.
    """

    def __init__(self):
        # Register all active security rule evaluators
        self.rules: List[BasePhishingRule] = [
            SPFFailureRule(),
            DKIMFailureRule(),
            DMARCFailureRule(),
            ReplyToMismatchRule(),
            DomainSimilarityRule(),
            SuspiciousTLDRule(),
            SuspiciousKeywordsRule(),
            URLShortenerRule(),
            NewlySeenSenderRule(),
        ]

    def analyze_email(self, email_data: Dict[str, Any], db: Session) -> Tuple[int, RiskLevel, List[str], str]:
        """
        Executes all active rules against the email data.
        Returns: (risk_score, risk_level, reasons_list, recommendation)
        """
        total_score = 0
        reasons: List[str] = []

        for rule in self.rules:
            score_addition, reason_desc = rule.evaluate(email_data, db)
            if score_addition > 0 and reason_desc:
                total_score += score_addition
                reasons.append(reason_desc)

        # Categorize Risk Level
        if total_score >= 60:
            risk_level = RiskLevel.HIGH_RISK
        elif total_score >= 30:
            risk_level = RiskLevel.MEDIUM_RISK
        else:
            risk_level = RiskLevel.SAFE

        # Generate Actionable Security Recommendation
        recommendation = self._generate_recommendation(risk_level, reasons)

        return total_score, risk_level, reasons, recommendation

    def _generate_recommendation(self, risk_level: RiskLevel, reasons: List[str]) -> str:
        """
        Generates tailored security advice based on detected threat reasons.
        """
        if risk_level == RiskLevel.SAFE:
            return "This email appears safe based on domain alignment and authentication checks."

        rec_parts = []
        
        reasons_text = " ".join(reasons)
        if "SPF Validation Failed" in reasons_text or "DMARC Validation Failed" in reasons_text:
            rec_parts.append("Do not click any links or download attachments before verifying sender identity out-of-band.")
        if "Reply-To Mismatch" in reasons_text:
            rec_parts.append("Verify the recipient email address before sending any sensitive information or credentials.")
        if "Lookalike Domain" in reasons_text:
            rec_parts.append("Warning: This email uses a lookalike domain imitating a trusted organization.")
        if "URL Shortener" in reasons_text:
            rec_parts.append("Do not open shortened links as they may bypass security filters.")

        if not rec_parts:
            if risk_level == RiskLevel.HIGH_RISK:
                rec_parts.append("High risk phishing indicator detected. Exercise extreme caution and do not reply.")
            else:
                rec_parts.append("Proceed with caution. Verify the sender's identity through official channels.")

        return " ".join(rec_parts)
