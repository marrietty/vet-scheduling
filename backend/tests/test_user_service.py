"""Unit tests for UserService profile methods."""
import pytest
import uuid
from unittest.mock import Mock, MagicMock
from datetime import datetime, timezone

from app.features.users.service import UserService
from app.features.users.repository import UserRepository
from app.features.users.models import User
from app.features.users.schemas import UserProfileResponse, UserProfileUpdate
from app.common.exceptions import NotFoundException, BadRequestException
# Import Pet and Appointment to resolve relationships in User model
from app.features.pets.models import Pet
from app.features.appointments.models import Appointment


@pytest.fixture(name="mock_repository")
def mock_repository_fixture():
    """Create a mock UserRepository."""
    return Mock(spec=UserRepository)


@pytest.fixture(name="service")
def service_fixture(mock_repository: UserRepository):
    """Create a UserService instance with mock repository."""
    return UserService(user_repo=mock_repository)


@pytest.fixture(name="test_user")
def test_user_fixture():
    """Create a test user object."""
    return User(
        id=uuid.uuid4(),
        full_name="Test User",
        email="test@example.com",
        hashed_password="hashed_password_here",
        role="pet_owner",
        phone="555-1234",
        city="Test City",
        preferences={"theme": "dark", "notifications": True},
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )


class TestGetCurrentUserProfile:
    """Tests for get_current_user_profile method."""
    
    def test_returns_profile_when_user_exists(
        self, service: UserService, mock_repository: Mock, test_user: User
    ):
        """Test that get_current_user_profile returns profile when user exists.
        
        Requirements: 2.1
        """
        # Arrange
        mock_repository.get_user_profile.return_value = test_user
        
        # Act
        result = service.get_current_user_profile(test_user.id)
        
        # Assert
        assert isinstance(result, UserProfileResponse)
        assert result.id == test_user.id
        assert result.full_name == test_user.full_name
        assert result.email == test_user.email
        assert result.phone == test_user.phone
        assert result.city == test_user.city
        assert result.role == test_user.role
        assert result.is_active == test_user.is_active
        assert result.preferences == test_user.preferences
        mock_repository.get_user_profile.assert_called_once_with(test_user.id)
    
    def test_excludes_sensitive_fields(
        self, service: UserService, mock_repository: Mock, test_user: User
    ):
        """Test that get_current_user_profile excludes sensitive fields like hashed_password.
        
        Requirements: 2.2
        """
        # Arrange
        mock_repository.get_user_profile.return_value = test_user
        
        # Act
        result = service.get_current_user_profile(test_user.id)
        
        # Assert
        assert not hasattr(result, "hashed_password")
        # Verify the result is a Pydantic model, not the ORM model
        assert isinstance(result, UserProfileResponse)
    
    def test_raises_not_found_when_user_does_not_exist(
        self, service: UserService, mock_repository: Mock
    ):
        """Test that get_current_user_profile raises NotFoundException when user doesn't exist.
        
        Requirements: 2.1
        """
        # Arrange
        user_id = uuid.uuid4()
        mock_repository.get_user_profile.return_value = None
        
        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            service.get_current_user_profile(user_id)
        
        assert "User not found" in str(exc_info.value.detail)
        mock_repository.get_user_profile.assert_called_once_with(user_id)


class TestUpdateUserProfile:
    """Tests for update_user_profile method."""
    
    def test_updates_full_name_successfully(
        self, service: UserService, mock_repository: Mock, test_user: User
    ):
        """Test that update_user_profile updates full_name field.
        
        Requirements: 3.1
        """
        # Arrange
        mock_repository.get_user_profile.return_value = test_user
        updated_user = User(**test_user.model_dump())
        updated_user.full_name = "Updated Name"
        mock_repository.update_user_profile.return_value = updated_user
        
        updates = UserProfileUpdate(full_name="Updated Name")
        
        # Act
        result = service.update_user_profile(test_user.id, updates)
        
        # Assert
        assert result.full_name == "Updated Name"
        mock_repository.update_user_profile.assert_called_once()
        call_args = mock_repository.update_user_profile.call_args
        assert call_args[0][0] == test_user.id
        assert call_args[0][1]["full_name"] == "Updated Name"
    
    def test_updates_email_when_unique(
        self, service: UserService, mock_repository: Mock, test_user: User
    ):
        """Test that update_user_profile updates email when it's unique.
        
        Requirements: 3.2
        """
        # Arrange
        mock_repository.get_user_profile.return_value = test_user
        mock_repository.email_exists_for_other_user.return_value = False
        updated_user = User(**test_user.model_dump())
        updated_user.email = "newemail@example.com"
        mock_repository.update_user_profile.return_value = updated_user
        
        updates = UserProfileUpdate(email="newemail@example.com")
        
        # Act
        result = service.update_user_profile(test_user.id, updates)
        
        # Assert
        assert result.email == "newemail@example.com"
        mock_repository.email_exists_for_other_user.assert_called_once_with(
            "newemail@example.com", test_user.id
        )
        mock_repository.update_user_profile.assert_called_once()
    
    def test_raises_bad_request_when_email_already_exists(
        self, service: UserService, mock_repository: Mock, test_user: User
    ):
        """Test that update_user_profile raises BadRequestException when email is already used.
        
        Requirements: 3.2
        """
        # Arrange
        mock_repository.get_user_profile.return_value = test_user
        mock_repository.email_exists_for_other_user.return_value = True
        
        updates = UserProfileUpdate(email="existing@example.com")
        
        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            service.update_user_profile(test_user.id, updates)
        
        assert "Email already in use" in str(exc_info.value.detail)
        mock_repository.email_exists_for_other_user.assert_called_once_with(
            "existing@example.com", test_user.id
        )
        mock_repository.update_user_profile.assert_not_called()
    
    def test_updates_phone_successfully(
        self, service: UserService, mock_repository: Mock, test_user: User
    ):
        """Test that update_user_profile updates phone field.
        
        Requirements: 3.3
        """
        # Arrange
        mock_repository.get_user_profile.return_value = test_user
        updated_user = User(**test_user.model_dump())
        updated_user.phone = "555-999-9999"
        mock_repository.update_user_profile.return_value = updated_user
        
        updates = UserProfileUpdate(phone="555-999-9999")
        
        # Act
        result = service.update_user_profile(test_user.id, updates)
        
        # Assert
        assert result.phone == "555-999-9999"
        mock_repository.update_user_profile.assert_called_once()
    
    def test_updates_city_successfully(
        self, service: UserService, mock_repository: Mock, test_user: User
    ):
        """Test that update_user_profile updates city field.
        
        Requirements: 3.4
        """
        # Arrange
        mock_repository.get_user_profile.return_value = test_user
        updated_user = User(**test_user.model_dump())
        updated_user.city = "New City"
        mock_repository.update_user_profile.return_value = updated_user
        
        updates = UserProfileUpdate(city="New City")
        
        # Act
        result = service.update_user_profile(test_user.id, updates)
        
        # Assert
        assert result.city == "New City"
        mock_repository.update_user_profile.assert_called_once()
    
    def test_updates_preferences_successfully(
        self, service: UserService, mock_repository: Mock, test_user: User
    ):
        """Test that update_user_profile updates preferences field.
        
        Requirements: 3.5
        """
        # Arrange
        mock_repository.get_user_profile.return_value = test_user
        new_preferences = {"theme": "light", "language": "en"}
        updated_user = User(**test_user.model_dump())
        updated_user.preferences = new_preferences
        mock_repository.update_user_profile.return_value = updated_user
        
        updates = UserProfileUpdate(preferences=new_preferences)
        
        # Act
        result = service.update_user_profile(test_user.id, updates)
        
        # Assert
        assert result.preferences == new_preferences
        mock_repository.update_user_profile.assert_called_once()
    
    def test_updates_multiple_fields_simultaneously(
        self, service: UserService, mock_repository: Mock, test_user: User
    ):
        """Test that update_user_profile can update multiple fields at once.
        
        Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
        """
        # Arrange
        mock_repository.get_user_profile.return_value = test_user
        mock_repository.email_exists_for_other_user.return_value = False
        
        updated_user = User(**test_user.model_dump())
        updated_user.full_name = "New Name"
        updated_user.email = "new@example.com"
        updated_user.phone = "555-000-0000"
        updated_user.city = "Another City"
        updated_user.preferences = {"new": "preferences"}
        mock_repository.update_user_profile.return_value = updated_user
        
        updates = UserProfileUpdate(
            full_name="New Name",
            email="new@example.com",
            phone="555-000-0000",
            city="Another City",
            preferences={"new": "preferences"}
        )
        
        # Act
        result = service.update_user_profile(test_user.id, updates)
        
        # Assert
        assert result.full_name == "New Name"
        assert result.email == "new@example.com"
        assert result.phone == "555-000-0000"
        assert result.city == "Another City"
        assert result.preferences == {"new": "preferences"}
        mock_repository.update_user_profile.assert_called_once()
    
    def test_returns_current_profile_when_no_updates_provided(
        self, service: UserService, mock_repository: Mock, test_user: User
    ):
        """Test that update_user_profile returns current profile when no updates provided."""
        # Arrange
        mock_repository.get_user_profile.return_value = test_user
        
        updates = UserProfileUpdate()  # No fields set
        
        # Act
        result = service.update_user_profile(test_user.id, updates)
        
        # Assert
        assert result.id == test_user.id
        assert result.full_name == test_user.full_name
        assert result.email == test_user.email
        mock_repository.update_user_profile.assert_not_called()
    
    def test_raises_not_found_when_user_does_not_exist(
        self, service: UserService, mock_repository: Mock
    ):
        """Test that update_user_profile raises NotFoundException when user doesn't exist.
        
        Requirements: 3.1
        """
        # Arrange
        user_id = uuid.uuid4()
        mock_repository.get_user_profile.return_value = None
        
        updates = UserProfileUpdate(full_name="New Name")
        
        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            service.update_user_profile(user_id, updates)
        
        assert "User not found" in str(exc_info.value.detail)
        mock_repository.update_user_profile.assert_not_called()
    
    def test_raises_not_found_when_user_disappears_during_update(
        self, service: UserService, mock_repository: Mock, test_user: User
    ):
        """Test that update_user_profile raises NotFoundException if user disappears during update."""
        # Arrange
        mock_repository.get_user_profile.return_value = test_user
        mock_repository.update_user_profile.return_value = None  # User disappeared
        
        updates = UserProfileUpdate(full_name="New Name")
        
        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            service.update_user_profile(test_user.id, updates)
        
        assert "User not found" in str(exc_info.value.detail)


class TestValidationIntegration:
    """Tests for validation logic integration with schemas."""
    
    def test_empty_name_validation_is_enforced(self, service: UserService):
        """Test that empty name validation from schema is enforced.
        
        Requirements: 3.1
        """
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            UserProfileUpdate(full_name="   ")  # Whitespace only
        
        assert "Full name cannot be empty" in str(exc_info.value)
    
    def test_invalid_email_format_validation_is_enforced(self, service: UserService):
        """Test that invalid email format validation from schema is enforced.
        
        Requirements: 3.2
        """
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            UserProfileUpdate(email="invalid-email")
        
        assert "Invalid email format" in str(exc_info.value)
    
    def test_invalid_phone_format_validation_is_enforced(self, service: UserService):
        """Test that invalid phone format validation from schema is enforced.
        
        Requirements: 3.3
        """
        # Act & Assert - too few digits
        with pytest.raises(ValueError) as exc_info:
            UserProfileUpdate(phone="123")
        
        assert "Phone number must contain 10-15 digits" in str(exc_info.value)
    
    def test_empty_city_validation_is_enforced(self, service: UserService):
        """Test that empty city validation from schema is enforced.
        
        Requirements: 4.4
        """
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            UserProfileUpdate(city="   ")  # Whitespace only
        
        assert "City cannot be empty" in str(exc_info.value)
    
    def test_valid_phone_formats_are_accepted(self, service: UserService):
        """Test that various valid phone formats are accepted.
        
        Requirements: 3.3
        """
        # Act & Assert - various valid formats
        valid_phones = [
            "1234567890",           # 10 digits
            "+1234567890",          # With country code
            "(123) 456-7890",       # US format
            "123-456-7890",         # Dashed format
            "+1 (123) 456-7890",    # Full international format
        ]
        
        for phone in valid_phones:
            update = UserProfileUpdate(phone=phone)
            assert update.phone == phone
