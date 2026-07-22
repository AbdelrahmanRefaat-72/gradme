"""
Authentication Header Rules (SPF, DKIM, DMARC).
Evaluates raw authentication headers for domain identity spoofing signatures.
"""

from typing import Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.services.rules.base_rule import BasePhishingRule
from app.utils.header_parser import parse_authentication_results


class SPFFailureRule(BasePhishingRule):
    rule_name = "SPF Failure"
    weight = 40

    def evaluate(self, email_data: Dict[str, Any], db: Session) -> Tuple[int, Optional[str]]:
        auth_raw = email_data.get("auth_headers_raw", "")
        parsed = parse_authentication_results(auth_raw)
        
        if parsed["spf"] == "fail":
            return self.weight, "SPF Validation Failed (Sender IP not authorized by domain SPF record)"
        return 0, None


class DKIMFailureRule(BasePhishingRule):
    rule_name = "DKIM Failure"
    weight = 20

    def evaluate(self, email_data: Dict[str, Any], db: Session) -> Tuple[int, Optional[str]]:
        auth_raw = email_data.get("auth_headers_raw", "")
        parsed = parse_authentication_results(auth_raw)
        
        if parsed["dkim"] == "fail":
            return self.weight, "DKIM Digital Signature Failed (Email body or headers altered in transit)"
        return 0, None


class DMARCFailureRule(BasePhishingRule):
    rule_name = "DMARC Failure"
    weight = 20

    def evaluate(self, email_data: Dict[str, Any], db: Session) -> Tuple[int, Optional[str]]:
        auth_raw = email_data.get("auth_headers_raw", "")
        parsed = parse_authentication_results(auth_raw)
        
        if parsed["dmarc"] == "fail":
            return self.weight, "DMARC Validation Failed (Header From address failed SPF/DKIM alignment checks)"
        return 0, None
