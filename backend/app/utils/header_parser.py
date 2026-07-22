"""
Header Parsing and Domain Utility Functions.
Extracts email addresses, domains, TLDs, and authentication header statuses.
"""

import re
from email.utils import parseaddr
from typing import Tuple, Optional, Dict


def extract_email_and_domain(raw_header: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts normalized (email_address, domain_name) from a header string (e.g. 'John Doe <john@company.com>').
    """
    if not raw_header:
        return None, None
    
    _, email_addr = parseaddr(raw_header)
    email_addr = email_addr.strip().lower()
    
    if not email_addr or "@" not in email_addr:
        return None, None
    
    domain = email_addr.split("@")[-1].lower()
    return email_addr, domain


def get_domain_tld(domain: Optional[str]) -> Optional[str]:
    """
    Extracts top-level domain from a domain string (e.g. 'company.com' -> '.com', 'alert.secure.xyz' -> '.xyz').
    """
    if not domain:
        return None
    parts = domain.lower().split(".")
    if len(parts) > 1:
        return f".{parts[-1]}"
    return None


def parse_authentication_results(auth_header: Optional[str]) -> Dict[str, str]:
    """
    Parses SPF, DKIM, and DMARC status values from raw Authentication-Results or Received-SPF headers.
    Returns dict: {"spf": "pass"|"fail"|"none"|"softfail", "dkim": "pass"|"fail"|"none", "dmarc": "pass"|"fail"|"none"}
    """
    results = {"spf": "none", "dkim": "none", "dmarc": "none"}
    if not auth_header:
        return results

    auth_lower = auth_header.lower()

    # Parse SPF
    if "spf=pass" in auth_lower or "spf=none" in auth_lower:
        results["spf"] = "pass"
    elif "spf=fail" in auth_lower or "spf=softfail" in auth_lower:
        results["spf"] = "fail"
    elif "received-spf: pass" in auth_lower:
        results["spf"] = "pass"
    elif "received-spf: fail" in auth_lower or "received-spf: softfail" in auth_lower:
        results["spf"] = "fail"

    # Parse DKIM
    if "dkim=pass" in auth_lower:
        results["dkim"] = "pass"
    elif "dkim=fail" in auth_lower:
        results["dkim"] = "fail"

    # Parse DMARC
    if "dmarc=pass" in auth_lower:
        results["dmarc"] = "pass"
    elif "dmarc=fail" in auth_lower:
        results["dmarc"] = "fail"

    return results


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Computes Levenshtein distance between two strings to identify lookalike / typosquatting domains.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]
