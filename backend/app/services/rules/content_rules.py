"""
Email Content & Text Analysis Rules.
Evaluates urgent subject/snippet keywords and hidden URL shorteners.
"""

from typing import Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.services.rules.base_rule import BasePhishingRule

# Urgent action keywords commonly found in social engineering & spear phishing
URGENT_PHISHING_KEYWORDS = [
    "account suspended", "verify your account", "urgent action required",
    "unauthorized login", "password reset required", "security alert",
    "wire transfer", "confirm your identity", "immediate payment",
    "billing issue", "update payment method", "gift card", "claim your reward",
    "suspicious activity detected", "account locked"
]

# URL Shortener domains used to obfuscate malicious phishing links
URL_SHORTENERS = [
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd",
    "buff.ly", "rebrand.ly", "cutt.ly", "shorturl.at"
]


class SuspiciousKeywordsRule(BasePhishingRule):
    rule_name = "Suspicious Urgency Keywords"
    weight = 15

    def evaluate(self, email_data: Dict[str, Any], db: Session) -> Tuple[int, Optional[str]]:
        subject = (email_data.get("subject") or "").lower()
        snippet = (email_data.get("snippet") or "").lower()
        content = f"{subject} {snippet}"

        detected_words = []
        for kw in URGENT_PHISHING_KEYWORDS:
            if kw in content:
                detected_words.append(kw)

        if detected_words:
            matched_str = ", ".join(f"'{w}'" for w in detected_words[:3])
            return self.weight, f"Urgent Social Engineering Keywords Detected ({matched_str})"
        return 0, None


class URLShortenerRule(BasePhishingRule):
    rule_name = "URL Shortener Detection"
    weight = 15

    def evaluate(self, email_data: Dict[str, Any], db: Session) -> Tuple[int, Optional[str]]:
        snippet = (email_data.get("snippet") or "").lower()
        body = (email_data.get("body_text") or "").lower()
        content = f"{snippet} {body}"

        for shortener in URL_SHORTENERS:
            if shortener in content:
                return self.weight, f"URL Shortener Obfuscation Detected (Contains shortlink domain '{shortener}')"
        return 0, None
