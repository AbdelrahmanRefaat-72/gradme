"""
Authentication API Router (v1).
Handles Google OAuth 2.0 login, callback handling, session status, and user profile endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.config.config import settings
from app.database.session import get_db
from app.services.gmail.auth_service import GmailAuthService
from app.schemas.user import UserRead
from app.models.user import User
from app.auth.security import get_current_user, create_access_token
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/google/login")
def google_oauth_login():
    """
    Redirects the client to Google's OAuth 2.0 consent screen.
    """
    auth_url = GmailAuthService.get_google_auth_url()
    return {"auth_url": auth_url}


@router.get("/google/callback")
async def google_oauth_callback(
    code: str = Query(..., description="Google OAuth authorization code"),
    error: str = Query(None, description="Google OAuth error message"),
    db: Session = Depends(get_db)
):
    """
    Handles Google OAuth 2.0 callback code, exchanges it for access/refresh tokens,
    saves user credentials, and redirects to frontend with session JWT token.
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google OAuth authorization error: {error}"
        )
    
    try:
        user, session_jwt = await GmailAuthService.process_oauth_callback(code, db)
        # Redirect to frontend dashboard with JWT token
        redirect_url = f"{settings.FRONTEND_URL}/auth-callback?token={session_jwt}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication callback failed: {str(e)}"
        )


@router.get("/me", response_model=UserRead)
def get_authenticated_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Returns profile information for the currently authenticated user.
    """
    return current_user


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logs out the user by invalidating authorization session.
    """
    return {"message": "Successfully logged out."}


@router.post("/dev-login", response_model=dict)
def dev_login_endpoint(
    email: str = Query("dev.user@emailguardian.local"),
    db: Session = Depends(get_db)
):
    """
    Development/Testing helper endpoint.
    Allows instant session creation in development environments without calling live Google OAuth APIs.
    """
    if settings.ENVIRONMENT != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dev login is disabled in production environments."
        )

    user = db.query(User).filter(User.email == email).first()
    now = datetime.utcnow()

    if not user:
        user = User(
            google_id=f"dev_google_id_{email}",
            email=email,
            full_name="Developer Account",
            picture_url="https://ui-avatars.com/api/?name=Developer+Account",
            last_login_at=now,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    session_jwt = create_access_token({"sub": str(user.id), "email": user.email})
    return {
        "access_token": session_jwt,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
        }
    }
