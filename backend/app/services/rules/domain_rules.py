"""
Domain & Header Alignment Rules.
Evaluates Reply-To mismatch, lookalike domain similarity (typosquatting), and suspicious TLDs.
"""

from typing import Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.services.rules.base_rule import BasePhishingRule
from app.utils.header_parser import extract_email_and_domain, get_domain_tld, levenshtein_distance

# High risk top-level domains frequently abused in phishing campaigns
SUSPICIOUS_TLDS = {
    ".zip", ".top", ".xyz", ".work", ".click", ".link", ".guru", 
    ".live", ".download", ".racing", ".country", ".stream", ".gq", ".cf", ".tk"
}

# Major brands commonly targeted by typosquatting attacks
TARGET_PROTECTED_DOMAINS = [
    "google.com", "gmail.com", "microsoft.com", "outlook.com", "apple.com", 
    "amazon.com", "paypal.com", "facebook.com", "netflix.com", "linkedin.com",
    "github.com", "bankofamerica.com", "chase.com", "wellsfargo.com"
]


class ReplyToMismatchRule(BasePhishingRule):
    rule_name = "Reply-To Mismatch"
    weight = 20

    def evaluate(self, email_data: Dict[str, Any], db: Session) -> Tuple[int, Optional[str]]:
        sender_header = email_data.get("sender", "")
        reply_to_header = email_data.get("reply_to", "")

        if not reply_to_header:
            return 0, None

        _, sender_domain = extract_email_and_domain(sender_header)
        _, reply_domain = extract_email_and_domain(reply_to_header)

        if sender_domain and reply_domain and sender_domain != reply_domain:
            return self.weight, f"Reply-To Mismatch (Replies will be directed to '{reply_domain}' instead of '{sender_domain}')"
        return 0, None


class DomainSimilarityRule(BasePhishingRule):
    rule_name = "Domain Similarity / Typosquatting"
    weight = 25

    def evaluate(self, email_data: Dict[str, Any], db: Session) -> Tuple[int, Optional[str]]:
        _, sender_domain = extract_email_and_domain(email_data.get("sender", ""))
        if not sender_domain:
            return 0, None

        sender_domain = sender_domain.lower()

        # If it's an exact match for a legitimate domain, it's not a lookalike
        if sender_domain in TARGET_PROTECTED_DOMAINS:
            return 0, None

        # Check Levenshtein distance for typosquatting (e.g. paypa1.com, g00gle.com, micros0ft.com)
        for target in TARGET_PROTECTED_DOMAINS:
            dist = levenshtein_distance(sender_domain, target)
            if 1 <= dist <= 2 and abs(len(sender_domain) - len(target)) <= 2:
                return self.weight, f"Lookalike Domain Detected ('{sender_domain}' closely imitates legitimate domain '{target}')"

        return 0, None


class SuspiciousTLDRule(BasePhishingRule):
    rule_name = "Suspicious TLD"
    weight = 15

    def evaluate(self, email_data: Dict[str, Any], db: Session) -> Tuple[int, Optional[str]]:
        _, sender_domain = extract_email_and_domain(email_data.get("sender", ""))
        tld = get_domain_tld(sender_domain)

        if tld in SUSPICIOUS_TLDS:
            return self.weight, f"High-Risk TLD Detected (Sender uses suspicious top-level domain '{tld}')"
        return 0, None
