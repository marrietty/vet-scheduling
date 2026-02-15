"""Token blacklist repository for database operations."""
from sqlmodel import Session, select
from datetime import datetime
from typing import Optional
import uuid

from app.features.auth.models import TokenBlacklist
from app.common.utils import get_pht_now


class TokenBlacklistRepository:
    """Repository for TokenBlacklist database operations.
    
    This class handles all database queries related to token blacklisting,
    following the repository pattern to abstract data access.
    
    Requirements:
        - 1.1: Add tokens to blacklist
        - 1.2: Check if tokens are blacklisted
        - 7.2: Check expiration when determining blacklist status
        - 7.4: Remove expired tokens from blacklist
    """
    
    def __init__(self, session: Session):
        """Initialize the repository with a database session.
        
        Args:
            session: SQLModel database session
        """
        self.session = session
    
    def add_token(self, token: str, expires_at: datetime, user_id: uuid.UUID) -> TokenBlacklist:
        """Add a token to the blacklist.
        
        Creates a new blacklist entry for the given token with its expiration
        timestamp and associated user ID.
        
        Args:
            token: The JWT token string to blacklist
            expires_at: When the token naturally expires
            user_id: UUID of the user who owns this token
            
        Returns:
            Created TokenBlacklist object with database-generated fields populated
            
        Requirements:
            - 1.1: Store invalidated tokens with expiration timestamp
            - 1.3: Store token value for authentication checks
        """
        blacklist_entry = TokenBlacklist(
            token=token,
            expires_at=expires_at,
            user_id=user_id
        )
        self.session.add(blacklist_entry)
        self.session.flush()
        self.session.refresh(blacklist_entry)
        return blacklist_entry
    
    def is_token_blacklisted(self, token: str) -> bool:
        """Check if a token is blacklisted and not expired.
        
        Queries the blacklist for the given token and checks if it exists
        and has not yet expired. Expired tokens are considered not blacklisted
        to allow natural token expiration to take precedence.
        
        Args:
            token: The JWT token string to check
            
        Returns:
            True if token is blacklisted and not expired, False otherwise
            
        Requirements:
            - 1.2: Check if tokens are blacklisted
            - 7.2: Ignore tokens whose expiration timestamp has passed
        """
        statement = select(TokenBlacklist).where(
            TokenBlacklist.token == token,
            TokenBlacklist.expires_at > get_pht_now()
        )
        result = self.session.exec(statement).first()
        return result is not None
    
    def remove_expired_tokens(self) -> int:
        """Remove all expired tokens from the blacklist.
        
        Deletes all blacklist entries where the expiration timestamp is
        earlier than the current time. This prevents the blacklist from
        growing indefinitely with old token records.
        
        Returns:
            Number of tokens removed from the blacklist
            
        Requirements:
            - 7.4: Delete all records where expiration timestamp is earlier than current time
        """
        # Find all expired tokens
        statement = select(TokenBlacklist).where(
            TokenBlacklist.expires_at < get_pht_now()
        )
        expired_tokens = self.session.exec(statement).all()
        
        # Delete each expired token
        count = 0
        for token in expired_tokens:
            self.session.delete(token)
            count += 1
        
        # Flush changes to database
        self.session.flush()
        
        return count
