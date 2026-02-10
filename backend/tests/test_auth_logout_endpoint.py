"""Integration tests for the logout endpoint."""

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


def test_logout_success(client: TestClient, test_user: dict):
    """
    Test successful logout with valid token.
    
    Requirements: 1.5, 1.1, 1.3
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Act
    response = client.post("/api/v1/auth/logout", headers=headers)
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Successfully logged out"}


def test_logout_without_token_fails(client: TestClient):
    """
    Test logout without authentication token fails.
    
    Requirements: 1.5
    """
    # Act
    response = client.post("/api/v1/auth/logout")
    
    # Assert
    assert response.status_code == 401  # HTTPBearer returns 401 for missing credentials


def test_logout_with_invalid_token_fails(client: TestClient):
    """
    Test logout with invalid token fails.
    
    Requirements: 1.4
    """
    # Arrange
    headers = {"Authorization": "Bearer invalid_token_here"}
    
    # Act
    response = client.post("/api/v1/auth/logout", headers=headers)
    
    # Assert
    assert response.status_code == 401


def test_logout_then_use_token_fails(client: TestClient, test_user: dict):
    """
    Test that using a token after logout fails.
    
    This verifies the complete logout flow:
    1. User logs out (token is blacklisted)
    2. User tries to use the same token (should fail)
    
    Requirements: 1.1, 1.2
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Act - First logout
    logout_response = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_response.status_code == 200
    
    # Act - Try to use the same token again (should fail because it's blacklisted)
    # We'll try to logout again with the same token
    second_logout_response = client.post("/api/v1/auth/logout", headers=headers)
    
    # Assert - Should fail with 401 because token is blacklisted
    assert second_logout_response.status_code == 401
    data = second_logout_response.json()
    assert "invalidated" in data["detail"].lower()
    # Verify error response format includes timestamp and error_type
    assert "timestamp" in data
    assert "error_type" in data
    assert data["error_type"] == "token_blacklisted"
