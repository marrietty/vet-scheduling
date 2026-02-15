"""Token blacklist model for the vet clinic system."""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

from app.common.utils import get_pht_now


class TokenBlacklist(SQLModel, table=True):
    """Token blacklist model for invalidated JWT tokens.
    
    This model stores tokens that have been explicitly invalidated through logout,
    preventing their reuse even if they haven't expired yet. Tokens are stored
    with their expiration time to enable periodic cleanup of expired entries.
    
    Attributes:
        id: Unique identifier for the blacklist entry
        token: The full JWT token string that has been invalidated
        expires_at: When the token naturally expires (for cleanup purposes)
        blacklisted_at: Timestamp when the token was added to the blacklist
        user_id: Foreign key to the user who owned this token
    
    Requirements:
        - 1.1: Store invalidated tokens with expiration timestamp
        - 1.3: Store token value for authentication checks
    """
    __tablename__ = "token_blacklist"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    token: str = Field(unique=True, index=True, nullable=False)
    expires_at: datetime = Field(nullable=False, index=True)
    blacklisted_at: datetime = Field(default_factory=get_pht_now, nullable=False)
    
    # Foreign key
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, nullable=False)
