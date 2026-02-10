"""Unit tests for TokenBlacklist model."""
import pytest
from datetime import datetime, timedelta
import uuid
from sqlmodel import Session, create_engine, SQLModel, select
from app.features.auth.models import TokenBlacklist
from app.features.users.models import User
from app.features.pets.models import Pet
from app.features.appointments.models import Appointment


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


def test_token_blacklist_creation(session: Session):
    """Test creating a TokenBlacklist entry."""
    # Arrange
    token = "test.jwt.token"
    expires_at = datetime.utcnow() + timedelta(hours=1)
    user_id = session.info['test_user_id']
    
    # Act
    blacklist_entry = TokenBlacklist(
        token=token,
        expires_at=expires_at,
        user_id=user_id
    )
    session.add(blacklist_entry)
    session.commit()
    session.refresh(blacklist_entry)
    
    # Assert
    assert blacklist_entry.id is not None
    assert blacklist_entry.token == token
    assert blacklist_entry.expires_at == expires_at
    assert blacklist_entry.user_id == user_id
    assert blacklist_entry.blacklisted_at is not None
    assert isinstance(blacklist_entry.blacklisted_at, datetime)


def test_token_blacklist_default_blacklisted_at(session: Session):
    """Test that blacklisted_at is automatically set to current time."""
    # Arrange
    before_creation = datetime.utcnow()
    user_id = session.info['test_user_id']
    
    # Act
    blacklist_entry = TokenBlacklist(
        token="test.token.2",
        expires_at=datetime.utcnow() + timedelta(hours=1),
        user_id=user_id
    )
    session.add(blacklist_entry)
    session.commit()
    session.refresh(blacklist_entry)
    
    after_creation = datetime.utcnow()
    
    # Assert
    assert blacklist_entry.blacklisted_at >= before_creation
    assert blacklist_entry.blacklisted_at <= after_creation


def test_token_blacklist_model_structure():
    """Test that the model has the correct structure and field definitions."""
    # Verify model has the expected fields
    assert 'id' in TokenBlacklist.model_fields
    assert 'token' in TokenBlacklist.model_fields
    assert 'expires_at' in TokenBlacklist.model_fields
    assert 'blacklisted_at' in TokenBlacklist.model_fields
    assert 'user_id' in TokenBlacklist.model_fields
    
    # Verify table name
    assert TokenBlacklist.__tablename__ == "token_blacklist"
