"""
Gmail API Service for Email Ingestion.
Fetches incoming emails from INBOX and SPAM folders using official Google Client API,
parses headers and MIME body (strictly omitting attachments), and triggers Threat Analysis.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from email.utils import parsedate_to_datetime
import base64
from sqlalchemy.orm import Session
from googleapiclient.discovery import build
from app.services.gmail.auth_service import GmailAuthService
from app.models.email import Email, EmailFolder
from app.models.suspicious_email import SuspiciousEmail
from app.services.rules.phishing_engine import PhishingEngineService


class GmailService:
    """
    Service for querying Gmail messages and integrating threat analysis.
    """

    @classmethod
    def get_gmail_client(cls, user_id: int, db: Session):
        """
        Retrieves an authenticated Google API Gmail v1 service instance.
        """
        creds = GmailAuthService.get_valid_google_credentials(user_id, db)
        return build("gmail", "v1", credentials=creds, cache_discovery=False)

    @classmethod
    def fetch_user_emails(
        cls, 
        user_id: int, 
        db: Session, 
        max_results: int = 15
    ) -> List[Email]:
        """
        Fetches recent emails from both INBOX and SPAM folders for a user.
        Parses headers, runs PhishingEngine threat evaluation, and saves to database.
        """
        try:
            service = cls.get_gmail_client(user_id, db)
        except Exception as e:
            print(f"[GmailService] Failed to obtain credentials for user_id={user_id}: {str(e)}")
            raise

        processed_emails: List[Email] = []
        folders_to_check = [("INBOX", EmailFolder.INBOX), ("SPAM", EmailFolder.SPAM)]

        for label, folder_enum in folders_to_check:
            try:
                # Query list of message IDs for folder
                response = service.users().messages().list(
                    userId="me",
                    labelIds=[label],
                    maxResults=max_results
                ).execute()

                messages = response.get("messages", [])
                for msg_summary in messages:
                    msg_id = msg_summary["id"]
                    
                    # Check if already processed in database
                    existing = db.query(Email).filter(Email.gmail_message_id == msg_id).first()
                    if existing:
                        processed_emails.append(existing)
                        continue

                    # Fetch full message details
                    full_msg = service.users().messages().get(
                        userId="me", 
                        id=msg_id, 
                        format="full"
                    ).execute()

                    email_obj = cls._parse_and_save_email(full_msg, user_id, folder_enum, db)
                    if email_obj:
                        processed_emails.append(email_obj)
            except Exception as err:
                print(f"[GmailService] Error fetching label '{label}' for user_id={user_id}: {str(err)}")
                raise RuntimeError(f"Unable to read the Gmail {label.lower()} folder.") from err

        return processed_emails

    @classmethod
    def _parse_and_save_email(
        cls, 
        msg: Dict[str, Any], 
        user_id: int, 
        folder: EmailFolder, 
        db: Session
    ) -> Optional[Email]:
        """
        Extracts headers, snippet, and body text from a raw Gmail API message object.
        Executes Phishing Engine rules and persists Email & SuspiciousEmail records.
        """
        msg_id = msg["id"]
        thread_id = msg.get("threadId")
        snippet = msg.get("snippet", "")
        payload = msg.get("payload", {})
        headers_list = payload.get("headers", [])

        # Parse header values
        headers_dict = {h["name"].lower(): h["value"] for h in headers_list}

        sender = headers_dict.get("from", "Unknown Sender")
        reply_to = headers_dict.get("reply-to")
        subject = headers_dict.get("subject", "(No Subject)")
        raw_date = headers_dict.get("date")

        # Combine authentication headers for security inspection
        auth_headers_parts = []
        if "authentication-results" in headers_dict:
            auth_headers_parts.append(f"Authentication-Results: {headers_dict['authentication-results']}")
        if "received-spf" in headers_dict:
            auth_headers_parts.append(f"Received-SPF: {headers_dict['received-spf']}")
        
        auth_headers_raw = "\n".join(auth_headers_parts)

        # Parse received date
        received_date = datetime.utcnow()
        if raw_date:
            try:
                received_date = parsedate_to_datetime(raw_date).replace(tzinfo=None)
            except Exception:
                pass

        # Extract plain text body snippet (strictly skipping attachments)
        body_text = cls._extract_plain_text_body(payload) or snippet

        # Construct raw email payload dict for Phishing Engine
        email_payload = {
            "user_id": user_id,
            "sender": sender,
            "reply_to": reply_to,
            "subject": subject,
            "snippet": snippet,
            "body_text": body_text,
            "auth_headers_raw": auth_headers_raw,
        }

        # Run Rule-Based Phishing Engine
        engine = PhishingEngineService()
        risk_score, risk_level, reasons, recommendation = engine.analyze_email(email_payload, db)
        is_suspicious = (risk_score >= 30)

        # Persist Email Record
        email_record = Email(
            user_id=user_id,
            gmail_message_id=msg_id,
            gmail_thread_id=thread_id,
            sender=sender,
            reply_to=reply_to,
            subject=subject,
            snippet=snippet,
            body_text=body_text[:5000],  # Truncate for database optimization
            received_date=received_date,
            folder=folder,
            auth_headers_raw=auth_headers_raw,
            is_suspicious=is_suspicious,
            is_expected=False,  # Will be updated by ExpectedEmailService in Phase 4
        )
        db.add(email_record)
        db.flush()

        # If risk score > 0, store SuspiciousEmail details
        if risk_score > 0:
            suspicious_record = SuspiciousEmail(
                email_id=email_record.id,
                risk_score=risk_score,
                risk_level=risk_level,
                reasons=reasons,
                recommendation=recommendation,
            )
            db.add(suspicious_record)

        db.commit()
        db.refresh(email_record)

        return email_record

    @classmethod
    def _extract_plain_text_body(cls, payload: Dict[str, Any]) -> str:
        """
        Recursively extracts plain text from MIME multipart payload without loading attachments.
        """
        mime_type = payload.get("mimeType", "")

        if mime_type == "text/plain":
            data = payload.get("body", {}).get("data")
            if data:
                return base64.urlsafe_b64decode(data.encode("ASCII")).decode("utf-8", errors="ignore")

        parts = payload.get("parts", [])
        for part in parts:
            part_mime = part.get("mimeType", "")
            if part_mime == "text/plain":
                data = part.get("body", {}).get("data")
                if data:
                    return base64.urlsafe_b64decode(data.encode("ASCII")).decode("utf-8", errors="ignore")
            elif "parts" in part:
                res = cls._extract_plain_text_body(part)
                if res:
                    return res

        return ""
