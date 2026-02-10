"""Integration tests for appointment reschedule endpoint."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from datetime import datetime, timedelta, timezone
import uuid

from app.main import app
from app.core.database import get_session
from app.features.users.models import User
from app.features.pets.models import Pet
from app.features.appointments.models import Appointment
from app.features.clinic.models import ClinicStatus
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
    """Create a test user (pet owner) and return user with token."""
    user_repo = UserRepository(session)
    auth_service = AuthService(user_repo)
    
    # Register a test user
    user = auth_service.register(
        email="owner@example.com",
        password="testpassword123",
        full_name="Pet Owner"
    )
    session.commit()
    
    # Create a token for the user
    token = create_access_token({"sub": str(user.id), "role": user.role})
    
    return {"user": user, "token": token}


@pytest.fixture(name="other_user")
def other_user_fixture(session: Session):
    """Create another test user (pet owner)."""
    user_repo = UserRepository(session)
    auth_service = AuthService(user_repo)
    
    # Register another test user
    user = auth_service.register(
        email="other@example.com",
        password="testpassword123",
        full_name="Other Owner"
    )
    session.commit()
    
    # Create a token for the user
    token = create_access_token({"sub": str(user.id), "role": user.role})
    
    return {"user": user, "token": token}


@pytest.fixture(name="clinic_open")
def clinic_open_fixture(session: Session):
    """Create a clinic status indicating the clinic is open."""
    clinic_status = ClinicStatus(
        status="open",
        updated_by=uuid.uuid4()
    )
    session.add(clinic_status)
    session.commit()
    return clinic_status


@pytest.fixture(name="test_pet")
def test_pet_fixture(session: Session, test_user: dict):
    """Create a test pet owned by test_user."""
    pet = Pet(
        name="Fluffy",
        species="Dog",
        breed="Labrador",
        owner_id=test_user["user"].id
    )
    session.add(pet)
    session.commit()
    session.refresh(pet)
    return pet


@pytest.fixture(name="other_pet")
def other_pet_fixture(session: Session, other_user: dict):
    """Create a test pet owned by other_user."""
    pet = Pet(
        name="Whiskers",
        species="Cat",
        breed="Persian",
        owner_id=other_user["user"].id
    )
    session.add(pet)
    session.commit()
    session.refresh(pet)
    return pet


@pytest.fixture(name="scheduled_appointment")
def scheduled_appointment_fixture(session: Session, test_user: dict, test_pet: Pet):
    """Create a scheduled appointment for test_user's pet."""
    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    appointment = Appointment(
        pet_id=test_pet.id,
        user_id=test_user["user"].id,
        start_time=start_time,
        end_time=end_time,
        service_type="routine",
        status="scheduled",
        notes="Regular checkup"
    )
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


@pytest.fixture(name="confirmed_appointment")
def confirmed_appointment_fixture(session: Session, test_user: dict, test_pet: Pet):
    """Create a confirmed appointment for test_user's pet."""
    start_time = datetime.now(timezone.utc) + timedelta(days=2)
    end_time = start_time + timedelta(hours=1)
    
    appointment = Appointment(
        pet_id=test_pet.id,
        user_id=test_user["user"].id,
        start_time=start_time,
        end_time=end_time,
        service_type="vaccination",
        status="confirmed",
        notes="Annual vaccination"
    )
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


@pytest.fixture(name="completed_appointment")
def completed_appointment_fixture(session: Session, test_user: dict, test_pet: Pet):
    """Create a completed appointment for test_user's pet."""
    start_time = datetime.now(timezone.utc) - timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    appointment = Appointment(
        pet_id=test_pet.id,
        user_id=test_user["user"].id,
        start_time=start_time,
        end_time=end_time,
        service_type="routine",
        status="completed",
        notes="Completed checkup"
    )
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


def test_reschedule_appointment_success(
    client: TestClient,
    test_user: dict,
    test_pet: Pet,
    scheduled_appointment: Appointment,
    clinic_open: ClinicStatus
):
    """
    Test successful appointment rescheduling with valid data.
    
    Requirements: 6.1, 6.2, 6.5
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    new_start = datetime.now(timezone.utc) + timedelta(days=3)
    new_end = new_start + timedelta(hours=1)
    
    reschedule_data = {
        "start_time": new_start.isoformat(),
        "end_time": new_end.isoformat()
    }
    
    # Act
    response = client.patch(
        f"/api/v1/appointments/{scheduled_appointment.id}/reschedule",
        json=reschedule_data,
        headers=headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    
    # Verify times were updated (Requirement 6.5)
    assert data["id"] == str(scheduled_appointment.id)
    # Parse and compare datetimes (handle different timezone formats)
    response_start = datetime.fromisoformat(data["start_time"].replace("Z", "+00:00"))
    response_end = datetime.fromisoformat(data["end_time"].replace("Z", "+00:00"))
    # Make both timezone-aware for comparison
    if response_start.tzinfo is None:
        response_start = response_start.replace(tzinfo=timezone.utc)
    if response_end.tzinfo is None:
        response_end = response_end.replace(tzinfo=timezone.utc)
    assert response_start.replace(microsecond=0) == new_start.replace(microsecond=0)
    assert response_end.replace(microsecond=0) == new_end.replace(microsecond=0)


def test_reschedule_confirmed_appointment_success(
    client: TestClient,
    test_user: dict,
    test_pet: Pet,
    confirmed_appointment: Appointment,
    clinic_open: ClinicStatus
):
    """
    Test successful rescheduling of a confirmed appointment.
    
    Requirements: 6.8
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    new_start = datetime.now(timezone.utc) + timedelta(days=4)
    new_end = new_start + timedelta(hours=1)
    
    reschedule_data = {
        "start_time": new_start.isoformat(),
        "end_time": new_end.isoformat()
    }
    
    # Act
    response = client.patch(
        f"/api/v1/appointments/{confirmed_appointment.id}/reschedule",
        json=reschedule_data,
        headers=headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(confirmed_appointment.id)


def test_reschedule_appointment_without_authentication_fails(
    client: TestClient,
    scheduled_appointment: Appointment
):
    """
    Test that rescheduling without authentication fails.
    
    Requirements: 6.1
    """
    # Arrange
    new_start = datetime.now(timezone.utc) + timedelta(days=3)
    new_end = new_start + timedelta(hours=1)
    
    reschedule_data = {
        "start_time": new_start.isoformat(),
        "end_time": new_end.isoformat()
    }
    
    # Act
    response = client.patch(
        f"/api/v1/appointments/{scheduled_appointment.id}/reschedule",
        json=reschedule_data
    )
    
    # Assert
    assert response.status_code == 401


def test_reschedule_other_users_appointment_fails(
    client: TestClient,
    other_user: dict,
    test_pet: Pet,
    scheduled_appointment: Appointment,
    clinic_open: ClinicStatus
):
    """
    Test that users cannot reschedule appointments for pets they don't own.
    
    Requirements: 6.1
    """
    # Arrange
    token = other_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    new_start = datetime.now(timezone.utc) + timedelta(days=3)
    new_end = new_start + timedelta(hours=1)
    
    reschedule_data = {
        "start_time": new_start.isoformat(),
        "end_time": new_end.isoformat()
    }
    
    # Act
    response = client.patch(
        f"/api/v1/appointments/{scheduled_appointment.id}/reschedule",
        json=reschedule_data,
        headers=headers
    )
    
    # Assert
    assert response.status_code == 403
    assert "own pets" in response.json()["detail"].lower()


def test_reschedule_completed_appointment_fails(
    client: TestClient,
    test_user: dict,
    test_pet: Pet,
    completed_appointment: Appointment,
    clinic_open: ClinicStatus
):
    """
    Test that completed appointments cannot be rescheduled.
    
    Requirements: 6.8, 6.9
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    new_start = datetime.now(timezone.utc) + timedelta(days=3)
    new_end = new_start + timedelta(hours=1)
    
    reschedule_data = {
        "start_time": new_start.isoformat(),
        "end_time": new_end.isoformat()
    }
    
    # Act
    response = client.patch(
        f"/api/v1/appointments/{completed_appointment.id}/reschedule",
        json=reschedule_data,
        headers=headers
    )
    
    # Assert
    assert response.status_code == 400
    assert "cannot reschedule" in response.json()["detail"].lower()


def test_reschedule_with_end_before_start_fails(
    client: TestClient,
    test_user: dict,
    test_pet: Pet,
    scheduled_appointment: Appointment,
    clinic_open: ClinicStatus
):
    """
    Test that rescheduling with end_time before start_time fails validation.
    
    Requirements: 6.2
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    new_start = datetime.now(timezone.utc) + timedelta(days=3)
    new_end = new_start - timedelta(hours=1)  # End before start
    
    reschedule_data = {
        "start_time": new_start.isoformat(),
        "end_time": new_end.isoformat()
    }
    
    # Act
    response = client.patch(
        f"/api/v1/appointments/{scheduled_appointment.id}/reschedule",
        json=reschedule_data,
        headers=headers
    )
    
    # Assert
    assert response.status_code == 422
    assert "end_time must be after start_time" in str(response.json())


def test_reschedule_nonexistent_appointment_fails(
    client: TestClient,
    test_user: dict,
    clinic_open: ClinicStatus
):
    """
    Test that rescheduling a nonexistent appointment fails.
    
    Requirements: 6.1
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    nonexistent_id = uuid.uuid4()
    new_start = datetime.now(timezone.utc) + timedelta(days=3)
    new_end = new_start + timedelta(hours=1)
    
    reschedule_data = {
        "start_time": new_start.isoformat(),
        "end_time": new_end.isoformat()
    }
    
    # Act
    response = client.patch(
        f"/api/v1/appointments/{nonexistent_id}/reschedule",
        json=reschedule_data,
        headers=headers
    )
    
    # Assert
    assert response.status_code == 404


def test_reschedule_with_missing_start_time_fails(
    client: TestClient,
    test_user: dict,
    scheduled_appointment: Appointment
):
    """
    Test that rescheduling without start_time fails validation.
    
    Requirements: 6.2
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    new_end = datetime.now(timezone.utc) + timedelta(days=3, hours=1)
    
    reschedule_data = {
        "end_time": new_end.isoformat()
        # Missing start_time
    }
    
    # Act
    response = client.patch(
        f"/api/v1/appointments/{scheduled_appointment.id}/reschedule",
        json=reschedule_data,
        headers=headers
    )
    
    # Assert
    assert response.status_code == 422


def test_reschedule_with_missing_end_time_fails(
    client: TestClient,
    test_user: dict,
    scheduled_appointment: Appointment
):
    """
    Test that rescheduling without end_time fails validation.
    
    Requirements: 6.2
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    new_start = datetime.now(timezone.utc) + timedelta(days=3)
    
    reschedule_data = {
        "start_time": new_start.isoformat()
        # Missing end_time
    }
    
    # Act
    response = client.patch(
        f"/api/v1/appointments/{scheduled_appointment.id}/reschedule",
        json=reschedule_data,
        headers=headers
    )
    
    # Assert
    assert response.status_code == 422


def test_reschedule_updates_updated_at_timestamp(
    client: TestClient,
    test_user: dict,
    test_pet: Pet,
    scheduled_appointment: Appointment,
    clinic_open: ClinicStatus,
    session: Session
):
    """
    Test that rescheduling updates the updated_at timestamp.
    
    Requirements: 6.7
    """
    # Arrange
    token = test_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    original_updated_at = scheduled_appointment.updated_at
    
    new_start = datetime.now(timezone.utc) + timedelta(days=3)
    new_end = new_start + timedelta(hours=1)
    
    reschedule_data = {
        "start_time": new_start.isoformat(),
        "end_time": new_end.isoformat()
    }
    
    # Act
    response = client.patch(
        f"/api/v1/appointments/{scheduled_appointment.id}/reschedule",
        json=reschedule_data,
        headers=headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    
    # Parse the updated_at timestamp from response
    response_updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
    
    # Verify updated_at was changed (Requirement 6.7)
    assert response_updated_at > original_updated_at
