"""Unit tests for TokenBlacklistRepository."""
import pytest
from datetime import datetime, timedelta
import uuid
from sqlmodel import Session, create_engine, SQLModel

from app.features.auth.models import TokenBlacklist
from app.features.auth.repository import TokenBlacklistRepository
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


@pytest.fixture(name="repository")
def repository_fixture(session: Session):
    """Create a TokenBlacklistRepository instance."""
    return TokenBlacklistRepository(session)


def test_add_token(session: Session, repository: TokenBlacklistRepository):
    """Test adding a token to the blacklist.
    
    Requirements: 1.1, 1.3
    """
    # Arrange
    token = "test.jwt.token"
    expires_at = datetime.utcnow() + timedelta(hours=1)
    user_id = session.info['test_user_id']
    
    # Act
    result = repository.add_token(token, expires_at, user_id)
    session.commit()
    
    # Assert
    assert result.id is not None
    assert result.token == token
    assert result.expires_at == expires_at
    assert result.user_id == user_id
    assert result.blacklisted_at is not None
    assert isinstance(result.blacklisted_at, datetime)


def test_is_token_blacklisted_returns_true_for_valid_blacklisted_token(
    session: Session, repository: TokenBlacklistRepository
):
    """Test that is_token_blacklisted returns True for a blacklisted non-expired token.
    
    Requirements: 1.2
    """
    # Arrange
    token = "blacklisted.token"
    expires_at = datetime.utcnow() + timedelta(hours=1)
    user_id = session.info['test_user_id']
    
    repository.add_token(token, expires_at, user_id)
    session.commit()
    
    # Act
    result = repository.is_token_blacklisted(token)
    
    # Assert
    assert result is True


def test_is_token_blacklisted_returns_false_for_non_blacklisted_token(
    session: Session, repository: TokenBlacklistRepository
):
    """Test that is_token_blacklisted returns False for a token not in the blacklist.
    
    Requirements: 1.2
    """
    # Arrange
    token = "not.blacklisted.token"
    
    # Act
    result = repository.is_token_blacklisted(token)
    
    # Assert
    assert result is False


def test_is_token_blacklisted_returns_false_for_expired_token(
    session: Session, repository: TokenBlacklistRepository
):
    """Test that is_token_blacklisted returns False for an expired blacklisted token.
    
    Requirements: 7.2
    """
    # Arrange
    token = "expired.token"
    expires_at = datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
    user_id = session.info['test_user_id']
    
    repository.add_token(token, expires_at, user_id)
    session.commit()
    
    # Act
    result = repository.is_token_blacklisted(token)
    
    # Assert
    assert result is False


def test_remove_expired_tokens_removes_only_expired(
    session: Session, repository: TokenBlacklistRepository
):
    """Test that remove_expired_tokens removes only expired tokens.
    
    Requirements: 7.4
    """
    # Arrange
    user_id = session.info['test_user_id']
    
    # Add expired tokens
    expired_token_1 = "expired.token.1"
    expired_token_2 = "expired.token.2"
    repository.add_token(expired_token_1, datetime.utcnow() - timedelta(hours=2), user_id)
    repository.add_token(expired_token_2, datetime.utcnow() - timedelta(hours=1), user_id)
    
    # Add valid tokens
    valid_token_1 = "valid.token.1"
    valid_token_2 = "valid.token.2"
    repository.add_token(valid_token_1, datetime.utcnow() + timedelta(hours=1), user_id)
    repository.add_token(valid_token_2, datetime.utcnow() + timedelta(hours=2), user_id)
    
    session.commit()
    
    # Act
    count = repository.remove_expired_tokens()
    session.commit()
    
    # Assert
    assert count == 2
    
    # Verify expired tokens are removed
    assert repository.is_token_blacklisted(expired_token_1) is False
    assert repository.is_token_blacklisted(expired_token_2) is False
    
    # Verify valid tokens remain
    assert repository.is_token_blacklisted(valid_token_1) is True
    assert repository.is_token_blacklisted(valid_token_2) is True


def test_remove_expired_tokens_with_empty_blacklist(
    session: Session, repository: TokenBlacklistRepository
):
    """Test that remove_expired_tokens handles empty blacklist gracefully.
    
    Requirements: 7.4
    """
    # Act
    count = repository.remove_expired_tokens()
    session.commit()
    
    # Assert
    assert count == 0


def test_remove_expired_tokens_with_no_expired_tokens(
    session: Session, repository: TokenBlacklistRepository
):
    """Test that remove_expired_tokens doesn't remove valid tokens.
    
    Requirements: 7.4
    """
    # Arrange
    user_id = session.info['test_user_id']
    
    # Add only valid tokens
    valid_token_1 = "valid.token.1"
    valid_token_2 = "valid.token.2"
    repository.add_token(valid_token_1, datetime.utcnow() + timedelta(hours=1), user_id)
    repository.add_token(valid_token_2, datetime.utcnow() + timedelta(hours=2), user_id)
    
    session.commit()
    
    # Act
    count = repository.remove_expired_tokens()
    session.commit()
    
    # Assert
    assert count == 0
    
    # Verify valid tokens remain
    assert repository.is_token_blacklisted(valid_token_1) is True
    assert repository.is_token_blacklisted(valid_token_2) is True


def test_add_token_with_duplicate_token_raises_error(
    session: Session, repository: TokenBlacklistRepository
):
    """Test that adding a duplicate token raises an error due to unique constraint."""
    # Arrange
    token = "duplicate.token"
    expires_at = datetime.utcnow() + timedelta(hours=1)
    user_id = session.info['test_user_id']
    
    repository.add_token(token, expires_at, user_id)
    session.commit()
    
    # Act & Assert
    with pytest.raises(Exception):  # SQLAlchemy will raise an IntegrityError
        repository.add_token(token, expires_at, user_id)
        session.commit()
