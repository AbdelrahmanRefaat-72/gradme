"""
Google OAuth 2.0 & Gmail API Credentials Management Service.
Handles authorization flow, token exchange, credential persistence, and token refreshing.
"""

import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
from urllib.parse import urlencode
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from app.config.config import settings
from app.models.user import User
from app.models.oauth_token import OAuthToken

# Least privilege scopes required for email security monitoring
GMAIL_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly",
]


class GmailAuthorizationError(ValueError):
    """Raised when the connected Google account did not grant Gmail read access."""


GMAIL_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"


class GmailAuthService:
    """
    Service managing Google OAuth 2.0 flows and token lifecycles.
    """

    @staticmethod
    def get_google_auth_url(state: str = "security_guardian") -> str:
        """
        Generates the Google OAuth 2.0 consent screen URL.
        Requests offline access and consent prompt to ensure a refresh token is returned.
        """
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(GMAIL_SCOPES),
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
        # OAuth parameters must be URL encoded. In particular, the space-separated
        # scope value must not be assembled into a URL by hand.
        query_string = urlencode(params)
        return f"{base_url}?{query_string}"

    @staticmethod
    async def exchange_code_for_tokens(code: str) -> Dict[str, Any]:
        """
        Exchanges Google authorization code for access and refresh tokens via HTTP POST.
        """
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=payload)
            if response.status_code != 200:
                raise ValueError(f"Failed to exchange OAuth code: {response.text}")
            return response.json()

    @staticmethod
    async def get_user_info_from_google(access_token: str) -> Dict[str, Any]:
        """
        Fetches user profile (email, name, picture, google_id) from Google OAuth2 API.
        """
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(userinfo_url, headers=headers)
            if response.status_code != 200:
                raise ValueError(f"Failed to fetch Google user profile: {response.text}")
            return response.json()

    @classmethod
    async def process_oauth_callback(cls, code: str, db: Session) -> Tuple[User, str]:
        """
        Processes Google OAuth authorization code:
        1. Exchanges code for tokens.
        2. Retrieves user profile.
        3. Persists/updates User and OAuthToken entities in DB.
        4. Returns User object and session JWT token.
        """
        token_data = await cls.exchange_code_for_tokens(code)
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in", 3600)
        scopes = token_data.get("scope", " ".join(GMAIL_SCOPES))

        user_info = await cls.get_user_info_from_google(access_token)
        google_id = user_info.get("id")
        email = user_info.get("email")
        full_name = user_info.get("name")
        picture_url = user_info.get("picture")

        # 1. Fetch or create User
        user = db.query(User).filter(User.google_id == google_id).first()
        now = datetime.utcnow()

        if not user:
            user = User(
                google_id=google_id,
                email=email,
                full_name=full_name,
                picture_url=picture_url,
                last_login_at=now,
            )
            db.add(user)
            db.flush()  # Obtain user.id
        else:
            user.email = email
            user.full_name = full_name
            user.picture_url = picture_url
            user.last_login_at = now

        # 2. Fetch or create OAuthToken
        oauth_token = db.query(OAuthToken).filter(OAuthToken.user_id == user.id).first()
        expires_at = now + timedelta(seconds=expires_in)

        if not oauth_token:
            oauth_token = OAuthToken(
                user_id=user.id,
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=token_data.get("token_type", "Bearer"),
                expires_at=expires_at,
                scopes=scopes,
            )
            db.add(oauth_token)
        else:
            oauth_token.access_token = access_token
            # Google only returns refresh_token on initial consent unless re-prompted
            if refresh_token:
                oauth_token.refresh_token = refresh_token
            oauth_token.expires_at = expires_at
            oauth_token.scopes = scopes

        db.commit()
        db.refresh(user)

        # 3. Create Session JWT for frontend authorization
        from app.auth.security import create_access_token
        session_jwt = create_access_token({"sub": str(user.id), "email": user.email})
        return user, session_jwt

    @staticmethod
    def get_valid_google_credentials(user_id: int, db: Session) -> Credentials:
        """
        Retrieves active Google credentials for a user.
        If access token is expired, uses stored refresh token to auto-refresh access token.
        """
        token_record = db.query(OAuthToken).filter(OAuthToken.user_id == user_id).first()
        if not token_record:
            raise ValueError(f"No Google OAuth tokens found for user_id={user_id}")

        granted_scopes = set((token_record.scopes or "").split())
        if GMAIL_READONLY_SCOPE not in granted_scopes:
            raise GmailAuthorizationError(
                "Gmail access was not granted for this account. Sign out, then sign in "
                "again and approve the Gmail read-only permission."
            )

        creds = Credentials(
            token=token_record.access_token,
            refresh_token=token_record.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=token_record.scopes.split(" "),
        )

        # Check if token is expired or expiring within 60 seconds
        if token_record.expires_at <= datetime.utcnow() + timedelta(seconds=60):
            if not token_record.refresh_token:
                raise ValueError("Access token expired and no refresh token available. Re-authentication required.")
            
            creds.refresh(Request())
            # Update token record in database
            token_record.access_token = creds.token
            if creds.expiry:
                token_record.expires_at = creds.expiry
            else:
                token_record.expires_at = datetime.utcnow() + timedelta(seconds=3600)
            db.commit()

        return creds
