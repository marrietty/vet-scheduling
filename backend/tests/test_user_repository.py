"""Unit tests for UserRepository profile methods."""
import pytest
import uuid
from sqlmodel import Session, create_engine, SQLModel

from app.features.users.models import User
from app.features.users.repository import UserRepository
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
        yield session


@pytest.fixture(name="repository")
def repository_fixture(session: Session):
    """Create a UserRepository instance."""
    return UserRepository(session)


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session, repository: UserRepository):
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        full_name="Test User",
        email="test@example.com",
        hashed_password="hashed_password_here",
        role="pet_owner",
        phone="555-1234",
        city="Test City",
        preferences={"theme": "dark", "notifications": True},
        is_active=True
    )
    created_user = repository.create(user)
    session.commit()
    session.refresh(created_user)
    return created_user


def test_get_user_profile_returns_user_when_exists(
    session: Session, repository: UserRepository, test_user: User
):
    """Test that get_user_profile returns user when it exists.
    
    Requirements: 2.1
    """
    # Act
    result = repository.get_user_profile(test_user.id)
    
    # Assert
    assert result is not None
    assert result.id == test_user.id
    assert result.full_name == test_user.full_name
    assert result.email == test_user.email
    assert result.city == test_user.city
    assert result.preferences == test_user.preferences


def test_get_user_profile_returns_none_when_not_exists(
    session: Session, repository: UserRepository
):
    """Test that get_user_profile returns None when user doesn't exist.
    
    Requirements: 2.1
    """
    # Arrange
    non_existent_id = uuid.uuid4()
    
    # Act
    result = repository.get_user_profile(non_existent_id)
    
    # Assert
    assert result is None


def test_update_user_profile_updates_full_name(
    session: Session, repository: UserRepository, test_user: User
):
    """Test that update_user_profile updates full_name field.
    
    Requirements: 3.1
    """
    # Arrange
    updates = {"full_name": "Updated Name"}
    
    # Act
    result = repository.update_user_profile(test_user.id, updates)
    session.commit()
    session.refresh(result)
    
    # Assert
    assert result is not None
    assert result.full_name == "Updated Name"
    assert result.email == test_user.email  # Other fields unchanged


def test_update_user_profile_updates_email(
    session: Session, repository: UserRepository, test_user: User
):
    """Test that update_user_profile updates email field.
    
    Requirements: 3.2
    """
    # Arrange
    updates = {"email": "newemail@example.com"}
    
    # Act
    result = repository.update_user_profile(test_user.id, updates)
    session.commit()
    session.refresh(result)
    
    # Assert
    assert result is not None
    assert result.email == "newemail@example.com"
    assert result.full_name == test_user.full_name  # Other fields unchanged


def test_update_user_profile_updates_phone(
    session: Session, repository: UserRepository, test_user: User
):
    """Test that update_user_profile updates phone field.
    
    Requirements: 3.3
    """
    # Arrange
    updates = {"phone": "555-9999"}
    
    # Act
    result = repository.update_user_profile(test_user.id, updates)
    session.commit()
    session.refresh(result)
    
    # Assert
    assert result is not None
    assert result.phone == "555-9999"


def test_update_user_profile_updates_city(
    session: Session, repository: UserRepository, test_user: User
):
    """Test that update_user_profile updates city field.
    
    Requirements: 3.4
    """
    # Arrange
    updates = {"city": "New City"}
    
    # Act
    result = repository.update_user_profile(test_user.id, updates)
    session.commit()
    session.refresh(result)
    
    # Assert
    assert result is not None
    assert result.city == "New City"


def test_update_user_profile_updates_preferences(
    session: Session, repository: UserRepository, test_user: User
):
    """Test that update_user_profile updates preferences field.
    
    Requirements: 3.5
    """
    # Arrange
    new_preferences = {"theme": "light", "language": "en"}
    updates = {"preferences": new_preferences}
    
    # Act
    result = repository.update_user_profile(test_user.id, updates)
    session.commit()
    session.refresh(result)
    
    # Assert
    assert result is not None
    assert result.preferences == new_preferences


def test_update_user_profile_updates_multiple_fields(
    session: Session, repository: UserRepository, test_user: User
):
    """Test that update_user_profile can update multiple fields at once.
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
    """
    # Arrange
    updates = {
        "full_name": "New Name",
        "email": "new@example.com",
        "phone": "555-0000",
        "city": "Another City",
        "preferences": {"new": "preferences"}
    }
    
    # Act
    result = repository.update_user_profile(test_user.id, updates)
    session.commit()
    session.refresh(result)
    
    # Assert
    assert result is not None
    assert result.full_name == "New Name"
    assert result.email == "new@example.com"
    assert result.phone == "555-0000"
    assert result.city == "Another City"
    assert result.preferences == {"new": "preferences"}


def test_update_user_profile_returns_none_when_user_not_exists(
    session: Session, repository: UserRepository
):
    """Test that update_user_profile returns None when user doesn't exist.
    
    Requirements: 3.1
    """
    # Arrange
    non_existent_id = uuid.uuid4()
    updates = {"full_name": "New Name"}
    
    # Act
    result = repository.update_user_profile(non_existent_id, updates)
    
    # Assert
    assert result is None


def test_update_user_profile_ignores_invalid_fields(
    session: Session, repository: UserRepository, test_user: User
):
    """Test that update_user_profile ignores fields that don't exist on the model."""
    # Arrange
    updates = {
        "full_name": "Valid Update",
        "invalid_field": "Should be ignored"
    }
    
    # Act
    result = repository.update_user_profile(test_user.id, updates)
    session.commit()
    session.refresh(result)
    
    # Assert
    assert result is not None
    assert result.full_name == "Valid Update"
    assert not hasattr(result, "invalid_field")


def test_email_exists_for_other_user_returns_true_when_email_exists(
    session: Session, repository: UserRepository, test_user: User
):
    """Test that email_exists_for_other_user returns True when email is used by another user.
    
    Requirements: 3.2
    """
    # Arrange - Create another user with a different email
    other_user = User(
        id=uuid.uuid4(),
        full_name="Other User",
        email="other@example.com",
        hashed_password="hashed_password_here",
        role="pet_owner",
        is_active=True
    )
    repository.create(other_user)
    session.commit()
    
    # Act - Check if test_user's email exists for other_user
    result = repository.email_exists_for_other_user(test_user.email, other_user.id)
    
    # Assert
    assert result is True


def test_email_exists_for_other_user_returns_false_when_email_is_own(
    session: Session, repository: UserRepository, test_user: User
):
    """Test that email_exists_for_other_user returns False when checking own email.
    
    Requirements: 3.2
    """
    # Act - Check if test_user's email exists for test_user (should be False)
    result = repository.email_exists_for_other_user(test_user.email, test_user.id)
    
    # Assert
    assert result is False


def test_email_exists_for_other_user_returns_false_when_email_not_exists(
    session: Session, repository: UserRepository, test_user: User
):
    """Test that email_exists_for_other_user returns False when email doesn't exist.
    
    Requirements: 3.2
    """
    # Act
    result = repository.email_exists_for_other_user("nonexistent@example.com", test_user.id)
    
    # Assert
    assert result is False


def test_email_exists_for_other_user_with_multiple_users(
    session: Session, repository: UserRepository
):
    """Test email_exists_for_other_user with multiple users in database."""
    # Arrange - Create multiple users
    user1 = User(
        id=uuid.uuid4(),
        full_name="User 1",
        email="user1@example.com",
        hashed_password="hashed_password_here",
        role="pet_owner",
        is_active=True
    )
    user2 = User(
        id=uuid.uuid4(),
        full_name="User 2",
        email="user2@example.com",
        hashed_password="hashed_password_here",
        role="pet_owner",
        is_active=True
    )
    user3 = User(
        id=uuid.uuid4(),
        full_name="User 3",
        email="user3@example.com",
        hashed_password="hashed_password_here",
        role="admin",
        is_active=True
    )
    
    repository.create(user1)
    repository.create(user2)
    repository.create(user3)
    session.commit()
    
    # Act & Assert
    # User2 trying to use User1's email
    assert repository.email_exists_for_other_user(user1.email, user2.id) is True
    
    # User2 checking their own email
    assert repository.email_exists_for_other_user(user2.email, user2.id) is False
    
    # User3 trying to use User1's email
    assert repository.email_exists_for_other_user(user1.email, user3.id) is True
    
    # Checking non-existent email
    assert repository.email_exists_for_other_user("new@example.com", user1.id) is False
