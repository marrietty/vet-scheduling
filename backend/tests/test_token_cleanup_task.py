"""Unit tests for token cleanup background task.

This module tests the cleanup_expired_tokens background task function
to ensure it correctly removes expired tokens and logs the operation.

Requirements:
    - 7.3: Provide mechanism to periodically remove expired tokens
    - 7.4: Delete expired tokens from Token_Blacklist
"""

import pytest
from datetime import datetime, timedelta
import uuid
from sqlmodel import Session, create_engine, SQLModel

from app.features.auth.tasks import cleanup_expired_tokens
from app.features.auth.models import TokenBlacklist
from app.features.users.models import User
from app.features.pets.models import Pet  # Import Pet to resolve relationship
from app.features.appointments.models import Appointment  # Import Appointment to resolve relationships


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    # Import all models to ensure tables are created
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Create a test user for foreign key constraint
        test_user = User(
            id=uuid.uuid4(),
            full_name="Test User",
            email="test@example.com",
            hashed_password="hashed_password_here",
            role="pet_owner",
            is_active=True
        )
        session.add(test_user)
        session.commit()
        session.refresh(test_user)
        
        # Store user_id in session for tests to use
        session.info['test_user_id'] = test_user.id
        
        yield session


def test_cleanup_expired_tokens_removes_expired_tokens(session: Session):
    """Test that cleanup_expired_tokens removes only expired tokens.
    
    This test verifies that the background task correctly identifies and
    removes tokens whose expiration timestamp has passed, while leaving
    valid tokens in the blacklist.
    
    Requirements: 7.3, 7.4
    """
    # Arrange: Create expired and valid tokens
    user_id = session.info['test_user_id']
    
    # Expired token (expired 1 hour ago)
    expired_token = TokenBlacklist(
        token="expired.jwt.token",
        expires_at=datetime.utcnow() - timedelta(hours=1),
        user_id=user_id
    )
    
    # Valid token (expires in 1 hour)
    valid_token = TokenBlacklist(
        token="valid.jwt.token",
        expires_at=datetime.utcnow() + timedelta(hours=1),
        user_id=user_id
    )
    
    session.add(expired_token)
    session.add(valid_token)
    session.commit()
    
    # Act: Run cleanup task with the test session
    removed_count = cleanup_expired_tokens(session)
    
    # Assert: Verify only expired token was removed
    assert removed_count == 1
    
    # Refresh session to get updated data
    session.expire_all()
    
    # Verify expired token is gone
    from sqlmodel import select
    expired_result = session.exec(
        select(TokenBlacklist).where(TokenBlacklist.token == "expired.jwt.token")
    ).first()
    assert expired_result is None
    
    # Verify valid token still exists
    valid_result = session.exec(
        select(TokenBlacklist).where(TokenBlacklist.token == "valid.jwt.token")
    ).first()
    assert valid_result is not None


def test_cleanup_expired_tokens_with_empty_blacklist(session: Session):
    """Test that cleanup_expired_tokens handles empty blacklist gracefully.
    
    This test verifies that the cleanup task works correctly when there
    are no tokens in the blacklist, returning 0 without errors.
    
    Requirements: 7.4
    """
    # Act: Run cleanup task with the test session
    removed_count = cleanup_expired_tokens(session)
    
    # Assert: No tokens removed
    assert removed_count == 0


def test_cleanup_expired_tokens_with_no_expired_tokens(session: Session):
    """Test that cleanup_expired_tokens doesn't remove valid tokens.
    
    This test verifies that when all tokens in the blacklist are still
    valid (not expired), the cleanup task doesn't remove any tokens.
    
    Requirements: 7.4
    """
    # Arrange: Create only valid tokens
    user_id = session.info['test_user_id']
    
    valid_token1 = TokenBlacklist(
        token="valid1.jwt.token",
        expires_at=datetime.utcnow() + timedelta(hours=1),
        user_id=user_id
    )
    
    valid_token2 = TokenBlacklist(
        token="valid2.jwt.token",
        expires_at=datetime.utcnow() + timedelta(hours=2),
        user_id=user_id
    )
    
    session.add(valid_token1)
    session.add(valid_token2)
    session.commit()
    
    # Act: Run cleanup task with the test session
    removed_count = cleanup_expired_tokens(session)
    
    # Assert: No tokens removed
    assert removed_count == 0
    
    # Verify both tokens still exist
    from sqlmodel import select
    token1_result = session.exec(
        select(TokenBlacklist).where(TokenBlacklist.token == "valid1.jwt.token")
    ).first()
    assert token1_result is not None
    
    token2_result = session.exec(
        select(TokenBlacklist).where(TokenBlacklist.token == "valid2.jwt.token")
    ).first()
    assert token2_result is not None


def test_cleanup_expired_tokens_with_mixed_tokens(session: Session):
    """Test cleanup with multiple expired and valid tokens.
    
    This test verifies that the cleanup task correctly handles a blacklist
    with a mix of expired and valid tokens, removing only the expired ones.
    
    Requirements: 7.3, 7.4
    """
    # Arrange: Create multiple expired and valid tokens
    user_id = session.info['test_user_id']
    
    # Create 3 expired tokens
    for i in range(3):
        expired_token = TokenBlacklist(
            token=f"expired{i}.jwt.token",
            expires_at=datetime.utcnow() - timedelta(hours=i+1),
            user_id=user_id
        )
        session.add(expired_token)
    
    # Create 2 valid tokens
    for i in range(2):
        valid_token = TokenBlacklist(
            token=f"valid{i}.jwt.token",
            expires_at=datetime.utcnow() + timedelta(hours=i+1),
            user_id=user_id
        )
        session.add(valid_token)
    
    session.commit()
    
    # Act: Run cleanup task with the test session
    removed_count = cleanup_expired_tokens(session)
    
    # Assert: Verify 3 expired tokens were removed
    assert removed_count == 3
    
    # Verify all expired tokens are gone
    from sqlmodel import select
    for i in range(3):
        expired_result = session.exec(
            select(TokenBlacklist).where(TokenBlacklist.token == f"expired{i}.jwt.token")
        ).first()
        assert expired_result is None
    
    # Verify all valid tokens still exist
    for i in range(2):
        valid_result = session.exec(
            select(TokenBlacklist).where(TokenBlacklist.token == f"valid{i}.jwt.token")
        ).first()
        assert valid_result is not None


def test_cleanup_expired_tokens_returns_correct_count(session: Session):
    """Test that cleanup_expired_tokens returns the correct count of removed tokens.
    
    This test verifies that the return value accurately reflects the number
    of tokens that were removed from the blacklist.
    
    Requirements: 7.4
    """
    # Arrange: Create 5 expired tokens
    user_id = session.info['test_user_id']
    
    for i in range(5):
        expired_token = TokenBlacklist(
            token=f"expired{i}.jwt.token",
            expires_at=datetime.utcnow() - timedelta(minutes=i+1),
            user_id=user_id
        )
        session.add(expired_token)
    
    session.commit()
    
    # Act: Run cleanup task with the test session
    removed_count = cleanup_expired_tokens(session)
    
    # Assert: Verify count is correct
    assert removed_count == 5
