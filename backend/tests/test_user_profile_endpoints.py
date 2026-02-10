"""Integration tests for user profile endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.core.database import get_session
from app.features.users.models import User
from app.features.users.repository import UserRepository
from app.features.auth.service import AuthService
from app.infrastructure.auth import create_access_token


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database session override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a test user and return user with token."""
    user_repo = UserRepository(session)
    auth_service = AuthService(user_repo)
    
    # Register a test user
    user = auth_service.register(
        email="test@example.com",
        password="testpassword123",
        full_name="Test User"
    )
    session.commit()
    
    # Create a token for the user
    token = create_access_token({"sub": str(user.id), "role": user.role})
    
    return {"user": user, "token": token}


@pytest.fixture(name="second_user")
def second_user_fixture(session: Session):
    """Create a second test user."""
    user_repo = UserRepository(session)
    auth_service = AuthService(user_repo)
    
    # Register a second test user
    user = auth_service.register(
        email="second@example.com",
        password="testpassword123",
        full_name="Second User"
    )
    session.commit()
    
    # Create a token for the user
    token = create_access_token({"sub": str(user.id), "role": user.role})
    
    return {"user": user, "token": token}


def test_get_profile_success(client: TestClient, test_user: dict):
    """
    Test successful profile retrieval with valid authentication.
    
    Requirements: 2.1, 2.3
    """
    # Arrange
    token = test_user["token"]
    user = test_user["user"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Act
    response = client.get("/api/v1/users/profile", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    
    # Verify all required fields are present (Requirement 2.1)
    assert data["id"] == str(user.id)
    assert data["full_name"] == user.full_name
    assert data["email"] == user.email
    assert data["role"] == user.role
    assert data["is_active"] == user.is_active
    assert "created_at" in data
    
    # Optional fields
    assert "phone" in data
    assert "city" in data
    assert "preferences" in data


def test_get_profile_excludes_sensitive_data(client: TestClient, test_user: dict):
    """
    Test that profile response does not include sensitive data.
    
    Requirements: 2.2
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Act
    response = client.get("/api/v1/users/profile", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    
    # Verify sensitive fields are NOT present (Requirement 2.2)
    assert "hashed_password" not in data
    assert "password" not in data


def test_get_profile_without_authentication_fails(client: TestClient):
    """
    Test profile retrieval without authentication fails.
    
    Requirements: 2.4
    """
    # Act
    response = client.get("/api/v1/users/profile")
    
    # Assert
    assert response.status_code == 401


def test_update_profile_with_valid_data(client: TestClient, test_user: dict):
    """
    Test successful profile update with valid data.
    
    Requirements: 3.1, 3.3, 3.4, 3.5
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "full_name": "Updated Name",
        "phone": "+1234567890",
        "city": "New York",
        "preferences": {"theme": "dark", "notifications": True}
    }
    
    # Act
    response = client.patch("/api/v1/users/profile", json=update_data, headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    
    # Verify updates were applied
    assert data["full_name"] == "Updated Name"
    assert data["phone"] == "+1234567890"
    assert data["city"] == "New York"
    assert data["preferences"] == {"theme": "dark", "notifications": True}


def test_update_profile_with_empty_name_fails(client: TestClient, test_user: dict):
    """
    Test profile update with empty name fails.
    
    Requirements: 3.1, 3.8
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"full_name": "   "}  # Empty/whitespace only
    
    # Act
    response = client.patch("/api/v1/users/profile", json=update_data, headers=headers)
    
    # Assert
    assert response.status_code == 422  # Validation error


def test_update_profile_with_invalid_email_fails(client: TestClient, test_user: dict):
    """
    Test profile update with invalid email format fails.
    
    Requirements: 3.2, 3.8
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"email": "not-an-email"}  # Invalid format
    
    # Act
    response = client.patch("/api/v1/users/profile", json=update_data, headers=headers)
    
    # Assert
    assert response.status_code == 422  # Validation error


def test_update_profile_with_duplicate_email_fails(
    client: TestClient, 
    test_user: dict, 
    second_user: dict
):
    """
    Test profile update with duplicate email fails.
    
    Requirements: 3.2, 3.8
    """
    # Arrange
    token = test_user["token"]
    second_user_email = second_user["user"].email
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"email": second_user_email}  # Try to use second user's email
    
    # Act
    response = client.patch("/api/v1/users/profile", json=update_data, headers=headers)
    
    # Assert
    assert response.status_code == 400  # Bad request (email already in use)
    assert "email" in response.json()["detail"].lower()


def test_update_profile_without_authentication_fails(client: TestClient):
    """
    Test profile update without authentication fails.
    
    Requirements: 3.6
    """
    # Arrange
    update_data = {"full_name": "New Name"}
    
    # Act
    response = client.patch("/api/v1/users/profile", json=update_data)
    
    # Assert
    assert response.status_code == 401


def test_update_profile_with_invalid_phone_fails(client: TestClient, test_user: dict):
    """
    Test profile update with invalid phone format fails.
    
    Requirements: 3.3, 3.8
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"phone": "123"}  # Too short
    
    # Act
    response = client.patch("/api/v1/users/profile", json=update_data, headers=headers)
    
    # Assert
    assert response.status_code == 422  # Validation error


def test_update_profile_with_empty_city_fails(client: TestClient, test_user: dict):
    """
    Test profile update with empty city fails when provided.
    
    Requirements: 4.4, 3.8
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"city": "   "}  # Empty/whitespace only
    
    # Act
    response = client.patch("/api/v1/users/profile", json=update_data, headers=headers)
    
    # Assert
    assert response.status_code == 422  # Validation error


def test_update_profile_partial_update(client: TestClient, test_user: dict):
    """
    Test that partial profile updates work correctly.
    
    Only the provided fields should be updated, others should remain unchanged.
    
    Requirements: 3.4, 3.5
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    original_email = test_user["user"].email
    
    # Act - Update only city
    update_data = {"city": "Los Angeles"}
    response = client.patch("/api/v1/users/profile", json=update_data, headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    
    # Verify city was updated
    assert data["city"] == "Los Angeles"
    
    # Verify other fields remain unchanged
    assert data["email"] == original_email
    assert data["full_name"] == test_user["user"].full_name


def test_get_profile_after_update_shows_changes(client: TestClient, test_user: dict):
    """
    Test that profile changes persist and are visible on subsequent retrieval.
    
    Requirements: 3.4, 3.5
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "city": "Chicago",
        "preferences": {"language": "en", "timezone": "America/Chicago"}
    }
    
    # Act - Update profile
    update_response = client.patch("/api/v1/users/profile", json=update_data, headers=headers)
    assert update_response.status_code == 200
    
    # Act - Get profile
    get_response = client.get("/api/v1/users/profile", headers=headers)
    
    # Assert
    assert get_response.status_code == 200
    data = get_response.json()
    
    # Verify changes persisted
    assert data["city"] == "Chicago"
    assert data["preferences"] == {"language": "en", "timezone": "America/Chicago"}
