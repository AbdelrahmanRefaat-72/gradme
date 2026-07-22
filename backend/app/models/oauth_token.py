"""
OAuthToken entity ORM model.
Stores Google OAuth 2.0 credentials securely for Gmail API interactions.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin


class OAuthToken(Base, TimestampMixin):
    __tablename__ = "oauth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)  # Refresh token may be sent once during initial grant
    token_type = Column(String, default="Bearer", nullable=False)
    expires_at = Column(DateTime, nullable=False)
    scopes = Column(Text, nullable=False)

    # Relationships
    user = relationship("User", back_populates="oauth_token")
