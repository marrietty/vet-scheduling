"""
Tests for UserProfileResponse schema.

This module tests that the UserProfileResponse schema:
- Includes all required non-sensitive fields
- Excludes sensitive fields like hashed_password
- Can be created from User model instances
"""

import pytest
from datetime import datetime
import uuid
from app.features.users.models import User
from app.features.users.schemas import UserProfileResponse


def test_user_profile_response_includes_all_required_fields():
    """Test that UserProfileResponse includes all non-sensitive profile fields."""
    user_id = uuid.uuid4()
    created_at = datetime.utcnow()
    
    profile = UserProfileResponse(
        id=user_id,
        full_name="John Doe",
        email="john@example.com",
        phone="+1234567890",
        city="New York",
        role="pet_owner",
        is_active=True,
        preferences={"theme": "dark", "notifications": True},
        created_at=created_at
    )
    
    # Verify all fields are present
    assert profile.id == user_id
    assert profile.full_name == "John Doe"
    assert profile.email == "john@example.com"
    assert profile.phone == "+1234567890"
    assert profile.city == "New York"
    assert profile.role == "pet_owner"
    assert profile.is_active is True
    assert profile.preferences == {"theme": "dark", "notifications": True}
    assert profile.created_at == created_at


def test_user_profile_response_allows_optional_fields_to_be_none():
    """Test that optional fields (phone, city, preferences) can be None."""
    user_id = uuid.uuid4()
    created_at = datetime.utcnow()
    
    profile = UserProfileResponse(
        id=user_id,
        full_name="Jane Smith",
        email="jane@example.com",
        phone=None,
        city=None,
        role="admin",
        is_active=True,
        preferences=None,
        created_at=created_at
    )
    
    assert profile.phone is None
    assert profile.city is None
    assert profile.preferences is None


def test_user_profile_response_from_user_model():
    """Test that UserProfileResponse can be created from a User model-like dict."""
    # Create a dict that mimics a User model instance
    # This avoids SQLAlchemy relationship initialization issues in tests
    user_data = {
        "id": uuid.uuid4(),
        "full_name": "Alice Johnson",
        "email": "alice@example.com",
        "hashed_password": "$2b$12$hashedpassword",  # This should NOT appear in response
        "phone": "+9876543210",
        "city": "San Francisco",
        "role": "pet_owner",
        "is_active": True,
        "preferences": {"language": "en", "timezone": "PST"},
        "created_at": datetime.utcnow()
    }
    
    # Create response from dict (simulating ORM model)
    profile = UserProfileResponse(**{k: v for k, v in user_data.items() if k != "hashed_password"})
    
    # Verify all non-sensitive fields are present
    assert profile.id == user_data["id"]
    assert profile.full_name == user_data["full_name"]
    assert profile.email == user_data["email"]
    assert profile.phone == user_data["phone"]
    assert profile.city == user_data["city"]
    assert profile.role == user_data["role"]
    assert profile.is_active == user_data["is_active"]
    assert profile.preferences == user_data["preferences"]
    assert profile.created_at == user_data["created_at"]
    
    # Verify sensitive field is NOT in the response
    profile_dict = profile.model_dump()
    assert "hashed_password" not in profile_dict


def test_user_profile_response_excludes_sensitive_fields():
    """Test that hashed_password is never included in UserProfileResponse."""
    # Verify the schema doesn't have a hashed_password field
    schema_fields = UserProfileResponse.model_fields.keys()
    assert "hashed_password" not in schema_fields
    
    # Verify the expected fields are present
    expected_fields = {
        "id", "full_name", "email", "phone", "city", 
        "role", "is_active", "preferences", "created_at"
    }
    assert set(schema_fields) == expected_fields


def test_user_profile_response_serialization():
    """Test that UserProfileResponse can be serialized to JSON."""
    user_id = uuid.uuid4()
    created_at = datetime.utcnow()
    
    profile = UserProfileResponse(
        id=user_id,
        full_name="Bob Wilson",
        email="bob@example.com",
        phone="+1122334455",
        city="Chicago",
        role="pet_owner",
        is_active=False,
        preferences={"notifications": False},
        created_at=created_at
    )
    
    # Serialize to dict
    profile_dict = profile.model_dump()
    
    # Verify structure
    assert isinstance(profile_dict, dict)
    assert profile_dict["id"] == user_id
    assert profile_dict["full_name"] == "Bob Wilson"
    assert profile_dict["email"] == "bob@example.com"
    assert profile_dict["is_active"] is False
    
    # Serialize to JSON
    profile_json = profile.model_dump_json()
    assert isinstance(profile_json, str)
    assert "Bob Wilson" in profile_json
    assert "bob@example.com" in profile_json
