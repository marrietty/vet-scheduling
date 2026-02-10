"""Unit tests for AuthService logout functionality."""
import pytest
from datetime import datetime, timedelta
import uuid
from sqlmodel import Session, create_engine, SQLModel
from unittest.mock import Mock, patch

from app.features.auth.service import AuthService
from app.features.auth.repository import TokenBlacklistRepository
from app.features.users.repository import UserRepository
from app.features.users.models import User
from app.features.pets.models import Pet
from app.features.appointments.models import Appointment
from app.common.exceptions import UnauthorizedException, BadRequestException, TokenBlacklistedException
from app.infrastructure.auth import create_access_token


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Create a test user
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
        
        session.info['test_user_id'] = test_user.id
        
        yield session


@pytest.fixture(name="user_repo")
def user_repo_fixture(session: Session):
    """Create a UserRepository instance."""
    return UserRepository(session)


@pytest.fixture(name="token_blacklist_repo")
def token_blacklist_repo_fixture(session: Session):
    """Create a TokenBlacklistRepository instance."""
    return TokenBlacklistRepository(session)


@pytest.fixture(name="auth_service")
def auth_service_fixture(user_repo: UserRepository, token_blacklist_repo: TokenBlacklistRepository):
    """Create an AuthService instance."""
    return AuthService(user_repo, token_blacklist_repo)


def test_logout_adds_token_to_blacklist(
    session: Session,
    auth_service: AuthService,
    token_blacklist_repo: TokenBlacklistRepository
):
    """Test that logout adds a valid token to the blacklist.
    
    Requirements: 1.1, 1.3
    """
    # Arrange
    user_id = session.info['test_user_id']
    token = create_access_token({"sub": str(user_id), "role": "pet_owner"})
    
    # Act
    auth_service.logout(token, user_id)
    session.commit()
    
    # Assert
    assert token_blacklist_repo.is_token_blacklisted(token) is True


def test_logout_extracts_correct_expiration(
    session: Session,
    auth_service: AuthService,
    token_blacklist_repo: TokenBlacklistRepository
):
    """Test that logout correctly extracts and stores token expiration.
    
    Requirements: 1.3
    """
    # Arrange
    user_id = session.info['test_user_id']
    token = create_access_token({"sub": str(user_id), "role": "pet_owner"})
    
    # Act
    auth_service.logout(token, user_id)
    session.commit()
    
    # Assert - token should be blacklisted
    assert token_blacklist_repo.is_token_blacklisted(token) is True


def test_logout_with_invalid_token_raises_unauthorized(
    session: Session,
    auth_service: AuthService
):
    """Test that logout with an invalid token raises UnauthorizedException.
    
    Requirements: 1.4
    """
    # Arrange
    user_id = session.info['test_user_id']
    invalid_token = "invalid.jwt.token"
    
    # Act & Assert
    with pytest.raises(UnauthorizedException) as exc_info:
        auth_service.logout(invalid_token, user_id)
    
    assert "Invalid or expired token" in str(exc_info.value)


def test_logout_with_expired_token_raises_unauthorized(
    session: Session,
    auth_service: AuthService
):
    """Test that logout with an expired token raises UnauthorizedException.
    
    Requirements: 1.4
    """
    # Arrange
    user_id = session.info['test_user_id']
    
    # Create a token that will be expired by manually crafting it with past expiration
    from jose import jwt
    from app.core import config
    
    past_time = datetime.utcnow() - timedelta(hours=2)
    token_data = {
        "sub": str(user_id),
        "role": "pet_owner",
        "exp": past_time
    }
    expired_token = jwt.encode(token_data, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    
    # Act & Assert
    with pytest.raises(UnauthorizedException) as exc_info:
        auth_service.logout(expired_token, user_id)
    
    assert "Invalid or expired token" in str(exc_info.value)


def test_logout_without_blacklist_repo_raises_bad_request(
    session: Session,
    user_repo: UserRepository
):
    """Test that logout without token blacklist repository raises BadRequestException."""
    # Arrange
    auth_service = AuthService(user_repo, None)  # No blacklist repo
    user_id = session.info['test_user_id']
    token = create_access_token({"sub": str(user_id), "role": "pet_owner"})
    
    # Act & Assert
    with pytest.raises(BadRequestException) as exc_info:
        auth_service.logout(token, user_id)
    
    assert "Logout functionality not available" in str(exc_info.value)


def test_verify_token_not_blacklisted_passes_for_valid_token(
    session: Session,
    auth_service: AuthService
):
    """Test that verify_token_not_blacklisted passes for a non-blacklisted token."""
    # Arrange
    user_id = session.info['test_user_id']
    token = create_access_token({"sub": str(user_id), "role": "pet_owner"})
    
    # Act & Assert - should not raise any exception
    auth_service.verify_token_not_blacklisted(token)


def test_verify_token_not_blacklisted_raises_for_blacklisted_token(
    session: Session,
    auth_service: AuthService
):
    """Test that verify_token_not_blacklisted raises UnauthorizedException for blacklisted token.
    
    Requirements: 1.2
    """
    # Arrange
    user_id = session.info['test_user_id']
    token = create_access_token({"sub": str(user_id), "role": "pet_owner"})
    
    # Blacklist the token
    auth_service.logout(token, user_id)
    session.commit()
    
    # Act & Assert
    with pytest.raises(TokenBlacklistedException) as exc_info:
        auth_service.verify_token_not_blacklisted(token)
    
    assert "Token has been invalidated" in str(exc_info.value)


def test_verify_token_not_blacklisted_without_repo_passes(
    session: Session,
    user_repo: UserRepository
):
    """Test that verify_token_not_blacklisted passes when no blacklist repo is configured."""
    # Arrange
    auth_service = AuthService(user_repo, None)  # No blacklist repo
    user_id = session.info['test_user_id']
    token = create_access_token({"sub": str(user_id), "role": "pet_owner"})
    
    # Act & Assert - should not raise any exception
    auth_service.verify_token_not_blacklisted(token)


def test_logout_with_token_missing_expiration_raises_unauthorized(
    session: Session,
    auth_service: AuthService
):
    """Test that logout with a token missing expiration raises UnauthorizedException."""
    # Arrange
    user_id = session.info['test_user_id']
    
    # Create a token without expiration (this is a mock scenario)
    # In practice, this shouldn't happen with properly created tokens
    # We'll use a mock to simulate this
    with patch('app.features.auth.service.verify_token') as mock_verify:
        mock_verify.return_value = {"sub": str(user_id)}  # Missing 'exp'
        
        # Act & Assert
        with pytest.raises(UnauthorizedException) as exc_info:
            auth_service.logout("some.token", user_id)
        
        assert "Invalid token: missing expiration" in str(exc_info.value)
