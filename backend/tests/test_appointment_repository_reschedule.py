"""Unit tests for AppointmentRepository rescheduling methods."""
import pytest
from datetime import datetime, timedelta
import uuid
from sqlmodel import Session, create_engine, SQLModel

from app.features.appointments.models import Appointment
from app.features.appointments.repository import AppointmentRepository
from app.features.users.models import User
from app.features.pets.models import Pet


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
        
        # Create a test pet
        test_pet = Pet(
            id=uuid.uuid4(),
            name="Fluffy",
            species="Dog",
            breed="Labrador",
            owner_id=test_user.id
        )
        session.add(test_pet)
        session.commit()
        session.refresh(test_pet)
        
        # Store IDs in session for tests to use
        session.info['test_user_id'] = test_user.id
        session.info['test_pet_id'] = test_pet.id
        
        yield session


@pytest.fixture(name="repository")
def repository_fixture(session: Session):
    """Create an AppointmentRepository instance."""
    return AppointmentRepository(session)


def test_get_appointment_by_id_returns_appointment(
    session: Session, repository: AppointmentRepository
):
    """Test that get_appointment_by_id returns an appointment when it exists.
    
    Requirements: 6.5
    """
    # Arrange
    appointment = Appointment(
        id=uuid.uuid4(),
        start_time=datetime.utcnow() + timedelta(days=1),
        end_time=datetime.utcnow() + timedelta(days=1, hours=1),
        service_type="routine",
        status="scheduled",
        pet_id=session.info['test_pet_id'],
        user_id=session.info['test_user_id']
    )
    session.add(appointment)
    session.commit()
    
    # Act
    result = repository.get_appointment_by_id(appointment.id)
    
    # Assert
    assert result is not None
    assert result.id == appointment.id
    assert result.service_type == "routine"
    assert result.status == "scheduled"


def test_get_appointment_by_id_returns_none_for_nonexistent(
    session: Session, repository: AppointmentRepository
):
    """Test that get_appointment_by_id returns None for non-existent appointment.
    
    Requirements: 6.5
    """
    # Arrange
    nonexistent_id = uuid.uuid4()
    
    # Act
    result = repository.get_appointment_by_id(nonexistent_id)
    
    # Assert
    assert result is None


def test_check_time_slot_available_returns_true_for_empty_slot(
    session: Session, repository: AppointmentRepository
):
    """Test that check_time_slot_available returns True when no appointments overlap.
    
    Requirements: 6.3
    """
    # Arrange
    start_time = datetime.utcnow() + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    # Act
    result = repository.check_time_slot_available(start_time, end_time)
    
    # Assert
    assert result is True


def test_check_time_slot_available_returns_false_for_overlapping_appointment(
    session: Session, repository: AppointmentRepository
):
    """Test that check_time_slot_available returns False when appointments overlap.
    
    Requirements: 6.3
    """
    # Arrange
    base_time = datetime.utcnow() + timedelta(days=1)
    
    # Create an existing appointment
    existing_appointment = Appointment(
        id=uuid.uuid4(),
        start_time=base_time,
        end_time=base_time + timedelta(hours=1),
        service_type="routine",
        status="confirmed",
        pet_id=session.info['test_pet_id'],
        user_id=session.info['test_user_id']
    )
    session.add(existing_appointment)
    session.commit()
    
    # Try to check a slot that overlaps
    new_start = base_time + timedelta(minutes=30)
    new_end = new_start + timedelta(hours=1)
    
    # Act
    result = repository.check_time_slot_available(new_start, new_end)
    
    # Assert
    assert result is False


def test_check_time_slot_available_excludes_specified_appointment(
    session: Session, repository: AppointmentRepository
):
    """Test that check_time_slot_available excludes the specified appointment.
    
    This is important for rescheduling - we don't want to conflict with ourselves.
    
    Requirements: 6.3
    """
    # Arrange
    base_time = datetime.utcnow() + timedelta(days=1)
    
    # Create an appointment
    appointment = Appointment(
        id=uuid.uuid4(),
        start_time=base_time,
        end_time=base_time + timedelta(hours=1),
        service_type="routine",
        status="scheduled",
        pet_id=session.info['test_pet_id'],
        user_id=session.info['test_user_id']
    )
    session.add(appointment)
    session.commit()
    
    # Check the same time slot but exclude this appointment
    # Act
    result = repository.check_time_slot_available(
        base_time,
        base_time + timedelta(hours=1),
        exclude_appointment_id=appointment.id
    )
    
    # Assert
    assert result is True


def test_check_time_slot_available_ignores_cancelled_appointments(
    session: Session, repository: AppointmentRepository
):
    """Test that check_time_slot_available ignores cancelled appointments.
    
    Requirements: 6.3
    """
    # Arrange
    base_time = datetime.utcnow() + timedelta(days=1)
    
    # Create a cancelled appointment
    cancelled_appointment = Appointment(
        id=uuid.uuid4(),
        start_time=base_time,
        end_time=base_time + timedelta(hours=1),
        service_type="routine",
        status="cancelled",
        pet_id=session.info['test_pet_id'],
        user_id=session.info['test_user_id']
    )
    session.add(cancelled_appointment)
    session.commit()
    
    # Check the same time slot
    # Act
    result = repository.check_time_slot_available(base_time, base_time + timedelta(hours=1))
    
    # Assert
    assert result is True


def test_update_appointment_times_updates_times_and_timestamp(
    session: Session, repository: AppointmentRepository
):
    """Test that update_appointment_times updates start_time, end_time, and updated_at.
    
    Requirements: 6.5
    """
    # Arrange
    original_start = datetime.utcnow() + timedelta(days=1)
    original_end = original_start + timedelta(hours=1)
    
    appointment = Appointment(
        id=uuid.uuid4(),
        start_time=original_start,
        end_time=original_end,
        service_type="routine",
        status="scheduled",
        pet_id=session.info['test_pet_id'],
        user_id=session.info['test_user_id']
    )
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    
    original_updated_at = appointment.updated_at
    
    # Wait a tiny bit to ensure timestamp changes
    import time
    time.sleep(0.01)
    
    # New times
    new_start = datetime.utcnow() + timedelta(days=2)
    new_end = new_start + timedelta(hours=1)
    
    # Act
    result = repository.update_appointment_times(appointment.id, new_start, new_end)
    session.commit()
    session.refresh(result)
    
    # Assert
    assert result.id == appointment.id
    assert result.start_time == new_start
    assert result.end_time == new_end
    assert result.updated_at > original_updated_at


def test_update_appointment_times_raises_error_for_nonexistent_appointment(
    session: Session, repository: AppointmentRepository
):
    """Test that update_appointment_times raises ValueError for non-existent appointment.
    
    Requirements: 6.5
    """
    # Arrange
    nonexistent_id = uuid.uuid4()
    new_start = datetime.utcnow() + timedelta(days=1)
    new_end = new_start + timedelta(hours=1)
    
    # Act & Assert
    with pytest.raises(ValueError, match="not found"):
        repository.update_appointment_times(nonexistent_id, new_start, new_end)


def test_update_appointment_times_preserves_other_fields(
    session: Session, repository: AppointmentRepository
):
    """Test that update_appointment_times doesn't modify other appointment fields.
    
    Requirements: 6.5
    """
    # Arrange
    original_start = datetime.utcnow() + timedelta(days=1)
    original_end = original_start + timedelta(hours=1)
    
    appointment = Appointment(
        id=uuid.uuid4(),
        start_time=original_start,
        end_time=original_end,
        service_type="surgery",
        status="confirmed",
        notes="Important surgery",
        pet_id=session.info['test_pet_id'],
        user_id=session.info['test_user_id']
    )
    session.add(appointment)
    session.commit()
    
    # New times
    new_start = datetime.utcnow() + timedelta(days=2)
    new_end = new_start + timedelta(hours=1)
    
    # Act
    result = repository.update_appointment_times(appointment.id, new_start, new_end)
    session.commit()
    session.refresh(result)
    
    # Assert - other fields should remain unchanged
    assert result.service_type == "surgery"
    assert result.status == "confirmed"
    assert result.notes == "Important surgery"
    assert result.pet_id == session.info['test_pet_id']
    assert result.user_id == session.info['test_user_id']
