"""
Tests for UserProfileUpdate schema.

This module tests that the UserProfileUpdate schema:
- Allows all fields to be optional
- Validates full_name is not empty when provided
- Validates email format when provided
- Validates phone format when provided
- Validates city is not empty when provided
- Accepts valid preferences data
"""

import pytest
from pydantic import ValidationError
from app.features.users.schemas import UserProfileUpdate


class TestUserProfileUpdateOptionalFields:
    """Test that all fields in UserProfileUpdate are optional."""
    
    def test_empty_update_is_valid(self):
        """Test that an update with no fields is valid."""
        update = UserProfileUpdate()
        assert update.full_name is None
        assert update.email is None
        assert update.phone is None
        assert update.city is None
        assert update.preferences is None
    
    def test_partial_update_with_single_field(self):
        """Test that updating a single field is valid."""
        update = UserProfileUpdate(full_name="John Doe")
        assert update.full_name == "John Doe"
        assert update.email is None
        assert update.phone is None
        assert update.city is None
        assert update.preferences is None
    
    def test_partial_update_with_multiple_fields(self):
        """Test that updating multiple fields is valid."""
        update = UserProfileUpdate(
            full_name="Jane Smith",
            email="jane@example.com",
            city="New York"
        )
        assert update.full_name == "Jane Smith"
        assert update.email == "jane@example.com"
        assert update.city == "New York"
        assert update.phone is None
        assert update.preferences is None
    
    def test_update_with_all_fields(self):
        """Test that updating all fields is valid."""
        update = UserProfileUpdate(
            full_name="Alice Johnson",
            email="alice@example.com",
            phone="+1234567890",
            city="San Francisco",
            preferences={"theme": "dark", "notifications": True}
        )
        assert update.full_name == "Alice Johnson"
        assert update.email == "alice@example.com"
        assert update.phone == "+1234567890"
        assert update.city == "San Francisco"
        assert update.preferences == {"theme": "dark", "notifications": True}


class TestFullNameValidation:
    """Test full_name validation - Requirements 3.1."""
    
    def test_valid_full_name(self):
        """Test that valid full names are accepted."""
        update = UserProfileUpdate(full_name="John Doe")
        assert update.full_name == "John Doe"
    
    def test_full_name_with_special_characters(self):
        """Test that names with special characters are accepted."""
        update = UserProfileUpdate(full_name="Mary O'Brien-Smith")
        assert update.full_name == "Mary O'Brien-Smith"
    
    def test_empty_string_full_name_rejected(self):
        """Test that empty string for full_name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(full_name="")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("full_name",)
        assert "empty" in errors[0]["msg"].lower()
    
    def test_whitespace_only_full_name_rejected(self):
        """Test that whitespace-only full_name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(full_name="   ")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("full_name",)
        assert "empty" in errors[0]["msg"].lower()
    
    def test_tabs_and_newlines_full_name_rejected(self):
        """Test that full_name with only tabs/newlines is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(full_name="\t\n  \t")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("full_name",)


class TestEmailValidation:
    """Test email validation - Requirements 3.2."""
    
    def test_valid_email_formats(self):
        """Test that various valid email formats are accepted."""
        valid_emails = [
            "user@example.com",
            "john.doe@company.co.uk",
            "alice+tag@domain.org",
            "test_user@sub.domain.com",
            "123@numbers.com"
        ]
        
        for email in valid_emails:
            update = UserProfileUpdate(email=email)
            assert update.email == email
    
    def test_email_without_at_symbol_rejected(self):
        """Test that email without @ symbol is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(email="notanemail.com")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("email",)
        assert "email" in errors[0]["msg"].lower()
    
    def test_email_without_domain_rejected(self):
        """Test that email without domain is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(email="user@")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("email",)
    
    def test_email_without_username_rejected(self):
        """Test that email without username is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(email="@example.com")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("email",)
    
    def test_email_with_spaces_rejected(self):
        """Test that email with spaces is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(email="user name@example.com")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("email",)
    
    def test_email_without_tld_rejected(self):
        """Test that email without top-level domain is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(email="user@domain")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("email",)


class TestPhoneValidation:
    """Test phone validation - Requirements 3.3."""
    
    def test_valid_phone_formats(self):
        """Test that various valid phone formats are accepted."""
        valid_phones = [
            "+1234567890",           # International format
            "1234567890",            # 10 digits
            "(123) 456-7890",        # US format with parentheses
            "123-456-7890",          # US format with dashes
            "+44 20 1234 5678",      # UK format with spaces
            "+1 (555) 123-4567",     # Mixed format
            "555.123.4567",          # Dots
            "+123456789012345"       # 15 digits (max)
        ]
        
        for phone in valid_phones:
            update = UserProfileUpdate(phone=phone)
            assert update.phone == phone
    
    def test_phone_too_short_rejected(self):
        """Test that phone with less than 10 digits is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(phone="123456789")  # 9 digits
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("phone",)
        assert "10-15 digits" in errors[0]["msg"]
    
    def test_phone_too_long_rejected(self):
        """Test that phone with more than 15 digits is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(phone="+1234567890123456")  # 16 digits
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("phone",)
        assert "10-15 digits" in errors[0]["msg"]
    
    def test_phone_with_letters_rejected(self):
        """Test that phone with letters is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(phone="123-456-ABCD")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("phone",)
    
    def test_phone_with_only_special_characters_rejected(self):
        """Test that phone with only special characters is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(phone="()--++")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("phone",)


class TestCityValidation:
    """Test city validation - Requirements 4.4."""
    
    def test_valid_city_names(self):
        """Test that valid city names are accepted."""
        valid_cities = [
            "New York",
            "San Francisco",
            "Los Angeles",
            "Saint-Étienne",  # With special characters
            "São Paulo",      # With accents
            "O'Fallon"        # With apostrophe
        ]
        
        for city in valid_cities:
            update = UserProfileUpdate(city=city)
            assert update.city == city
    
    def test_empty_string_city_rejected(self):
        """Test that empty string for city is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(city="")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("city",)
        assert "empty" in errors[0]["msg"].lower()
    
    def test_whitespace_only_city_rejected(self):
        """Test that whitespace-only city is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(city="   ")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("city",)
        assert "empty" in errors[0]["msg"].lower()
    
    def test_tabs_and_newlines_city_rejected(self):
        """Test that city with only tabs/newlines is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(city="\t\n  ")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("city",)


class TestPreferencesValidation:
    """Test preferences validation - Requirements 8.1, 8.2."""
    
    def test_valid_preferences_dict(self):
        """Test that valid preferences dictionaries are accepted."""
        preferences = {
            "theme": "dark",
            "notifications": True,
            "language": "en",
            "timezone": "PST"
        }
        update = UserProfileUpdate(preferences=preferences)
        assert update.preferences == preferences
    
    def test_empty_preferences_dict(self):
        """Test that empty preferences dict is accepted."""
        update = UserProfileUpdate(preferences={})
        assert update.preferences == {}
    
    def test_nested_preferences_dict(self):
        """Test that nested preferences are accepted."""
        preferences = {
            "ui": {
                "theme": "dark",
                "fontSize": 14
            },
            "notifications": {
                "email": True,
                "push": False
            }
        }
        update = UserProfileUpdate(preferences=preferences)
        assert update.preferences == preferences
    
    def test_preferences_with_various_types(self):
        """Test that preferences can contain various data types."""
        preferences = {
            "string": "value",
            "number": 42,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "object": {"nested": "value"}
        }
        update = UserProfileUpdate(preferences=preferences)
        assert update.preferences == preferences


class TestSchemaIntegration:
    """Test overall schema behavior and integration."""
    
    def test_schema_serialization(self):
        """Test that schema can be serialized to dict."""
        update = UserProfileUpdate(
            full_name="Test User",
            email="test@example.com",
            phone="+1234567890",
            city="Test City",
            preferences={"key": "value"}
        )
        
        data = update.model_dump()
        assert isinstance(data, dict)
        assert data["full_name"] == "Test User"
        assert data["email"] == "test@example.com"
        assert data["phone"] == "+1234567890"
        assert data["city"] == "Test City"
        assert data["preferences"] == {"key": "value"}
    
    def test_schema_serialization_excludes_none_values(self):
        """Test that None values can be excluded from serialization."""
        update = UserProfileUpdate(full_name="Test User")
        
        # Include None values
        data_with_none = update.model_dump()
        assert data_with_none["email"] is None
        assert data_with_none["phone"] is None
        
        # Exclude None values
        data_without_none = update.model_dump(exclude_none=True)
        assert "email" not in data_without_none
        assert "phone" not in data_without_none
        assert data_without_none["full_name"] == "Test User"
    
    def test_multiple_validation_errors(self):
        """Test that multiple validation errors are reported together."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(
                full_name="",
                email="invalid-email",
                phone="123",
                city=""
            )
        
        errors = exc_info.value.errors()
        # Should have errors for full_name, email, phone, and city
        assert len(errors) == 4
        
        error_fields = {error["loc"][0] for error in errors}
        assert error_fields == {"full_name", "email", "phone", "city"}
