"""Unit tests for AppointmentService.reschedule_appointment method.

This module tests the business logic for appointment rescheduling including:
- Appointment existence validation
- Pet ownership validation
- Appointment status validation
- Clinic hours validation
- Time slot availability validation
- Successful rescheduling

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.7, 6.8
"""

import pytest
from datetime import datetime, timedelta
import uuid
from unittest.mock import Mock, MagicMock

from app.features.appointments.service import AppointmentService
from app.features.appointments.models import Appointment
from app.features.pets.models import Pet
from app.features.clinic.models import ClinicStatus
from app.common.exceptions import (
    NotFoundException,
    ForbiddenException,
    BadRequestException
)


@pytest.fixture
def mock_appointment_repo():
    """Create a mock AppointmentRepository."""
    return Mock()


@pytest.fixture
def mock_pet_repo():
    """Create a mock PetRepository."""
    return Mock()


@pytest.fixture
def mock_clinic_status_repo():
    """Create a mock ClinicStatusRepository."""
    return Mock()


@pytest.fixture
def appointment_service(mock_appointment_repo, mock_pet_repo, mock_clinic_status_repo):
    """Create an AppointmentService instance with mocked dependencies."""
    return AppointmentService(
        appointment_repo=mock_appointment_repo,
        pet_repo=mock_pet_repo,
        clinic_status_repo=mock_clinic_status_repo
    )


@pytest.fixture
def test_user_id():
    """Create a test user ID."""
    return uuid.uuid4()


@pytest.fixture
def test_pet_id():
    """Create a test pet ID."""
    return uuid.uuid4()


@pytest.fixture
def test_appointment_id():
    """Create a test appointment ID."""
    return uuid.uuid4()


@pytest.fixture
def test_appointment(test_appointment_id, test_pet_id, test_user_id):
    """Create a test appointment."""
    return Appointment(
        id=test_appointment_id,
        pet_id=test_pet_id,
        user_id=test_user_id,
        start_time=datetime.utcnow() + timedelta(days=1),
        end_time=datetime.utcnow() + timedelta(days=1, hours=1),
        service_type="routine",
        status="scheduled"
    )


@pytest.fixture
def test_pet(test_pet_id, test_user_id):
    """Create a test pet."""
    return Pet(
        id=test_pet_id,
        name="Fluffy",
        species="Dog",
        breed="Labrador",
        owner_id=test_user_id
    )


class TestAppointmentExistenceValidation:
    """Test that reschedule_appointment validates appointment exists.
    
    Requirements: 6.1
    """
    
    def test_reschedule_nonexistent_appointment_raises_not_found(
        self,
        appointment_service,
        mock_appointment_repo,
        test_appointment_id,
        test_user_id
    ):
        """Test that rescheduling a non-existent appointment raises NotFoundException."""
        # Arrange
        mock_appointment_repo.get_appointment_by_id.return_value = None
        new_start = datetime.utcnow() + timedelta(days=2)
        new_end = new_start + timedelta(hours=1)
        
        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            appointment_service.reschedule_appointment(
                test_appointment_id,
                test_user_id,
                new_start,
                new_end
            )
        
        assert "Appointment not found" in str(exc_info.value.detail)
        mock_appointment_repo.get_appointment_by_id.assert_called_once_with(test_appointment_id)


class TestPetOwnershipValidation:
    """Test that reschedule_appointment validates pet ownership.
    
    Requirements: 6.1
    """
    
    def test_reschedule_by_non_owner_raises_forbidden(
        self,
        appointment_service,
        mock_appointment_repo,
        mock_pet_repo,
        test_appointment,
        test_pet,
        test_appointment_id
    ):
        """Test that rescheduling by non-owner raises ForbiddenException."""
        # Arrange
        mock_appointment_repo.get_appointment_by_id.return_value = test_appointment
        mock_pet_repo.get_by_id.return_value = test_pet
        
        # Different user ID (not the owner)
        different_user_id = uuid.uuid4()
        new_start = datetime.utcnow() + timedelta(days=2)
        new_end = new_start + timedelta(hours=1)
        
        # Act & Assert
        with pytest.raises(ForbiddenException) as exc_info:
            appointment_service.reschedule_appointment(
                test_appointment_id,
                different_user_id,
                new_start,
                new_end
            )
        
        assert "You can only reschedule appointments for your own pets" in str(exc_info.value.detail)
    
    def test_reschedule_with_nonexistent_pet_raises_not_found(
        self,
        appointment_service,
        mock_appointment_repo,
        mock_pet_repo,
        test_appointment,
        test_appointment_id,
        test_user_id
    ):
        """Test that rescheduling with non-existent pet raises NotFoundException."""
        # Arrange
        mock_appointment_repo.get_appointment_by_id.return_value = test_appointment
        mock_pet_repo.get_by_id.return_value = None
        
        new_start = datetime.utcnow() + timedelta(days=2)
        new_end = new_start + timedelta(hours=1)
        
        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            appointment_service.reschedule_appointment(
                test_appointment_id,
                test_user_id,
                new_start,
                new_end
            )
        
        assert "Pet not found" in str(exc_info.value.detail)


class TestAppointmentStatusValidation:
    """Test that reschedule_appointment validates appointment status.
    
    Requirements: 6.8
    """
    
    @pytest.mark.parametrize("invalid_status", ["pending", "completed", "cancelled"])
    def test_reschedule_invalid_status_raises_bad_request(
        self,
        appointment_service,
        mock_appointment_repo,
        mock_pet_repo,
        test_appointment,
        test_pet,
        test_appointment_id,
        test_user_id,
        invalid_status
    ):
        """Test that rescheduling appointments with invalid status raises BadRequestException."""
        # Arrange
        test_appointment.status = invalid_status
        mock_appointment_repo.get_appointment_by_id.return_value = test_appointment
        mock_pet_repo.get_by_id.return_value = test_pet
        
        new_start = datetime.utcnow() + timedelta(days=2)
        new_end = new_start + timedelta(hours=1)
        
        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            appointment_service.reschedule_appointment(
                test_appointment_id,
                test_user_id,
                new_start,
                new_end
            )
        
        assert f"Cannot reschedule {invalid_status} appointments" in str(exc_info.value.detail)
    
    @pytest.mark.parametrize("valid_status", ["scheduled", "confirmed"])
    def test_reschedule_valid_status_proceeds(
        self,
        appointment_service,
        mock_appointment_repo,
        mock_pet_repo,
        mock_clinic_status_repo,
        test_appointment,
        test_pet,
        test_appointment_id,
        test_user_id,
        valid_status
    ):
        """Test that rescheduling appointments with valid status proceeds."""
        # Arrange
        test_appointment.status = valid_status
        mock_appointment_repo.get_appointment_by_id.return_value = test_appointment
        mock_pet_repo.get_by_id.return_value = test_pet
        
        # Mock clinic is open
        clinic_status = ClinicStatus(status="open", updated_at=datetime.utcnow())
        mock_clinic_status_repo.get_current_status.return_value = clinic_status
        
        # Mock time slot is available
        mock_appointment_repo.check_time_slot_available.return_value = True
        
        # Mock successful update
        updated_appointment = test_appointment
        mock_appointment_repo.update_appointment_times.return_value = updated_appointment
        
        new_start = datetime.utcnow() + timedelta(days=2)
        new_end = new_start + timedelta(hours=1)
        
        # Act
        result = appointment_service.reschedule_appointment(
            test_appointment_id,
            test_user_id,
            new_start,
            new_end
        )
        
        # Assert - should not raise exception
        assert result is not None


class TestClinicHoursValidation:
    """Test that reschedule_appointment validates clinic hours.
    
    Requirements: 6.4
    """
    
    def test_reschedule_when_clinic_closed_raises_bad_request(
        self,
        appointment_service,
        mock_appointment_repo,
        mock_pet_repo,
        mock_clinic_status_repo,
        test_appointment,
        test_pet,
        test_appointment_id,
        test_user_id
    ):
        """Test that rescheduling when clinic is closed raises BadRequestException."""
        # Arrange
        test_appointment.status = "scheduled"
        mock_appointment_repo.get_appointment_by_id.return_value = test_appointment
        mock_pet_repo.get_by_id.return_value = test_pet
        
        # Mock clinic is closed
        clinic_status = ClinicStatus(status="close", updated_at=datetime.utcnow())
        mock_clinic_status_repo.get_current_status.return_value = clinic_status
        
        new_start = datetime.utcnow() + timedelta(days=2)
        new_end = new_start + timedelta(hours=1)
        
        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            appointment_service.reschedule_appointment(
                test_appointment_id,
                test_user_id,
                new_start,
                new_end
            )
        
        assert "Clinic is closed during the requested time" in str(exc_info.value.detail)
    
    def test_reschedule_when_clinic_open_proceeds(
        self,
        appointment_service,
        mock_appointment_repo,
        mock_pet_repo,
        mock_clinic_status_repo,
        test_appointment,
        test_pet,
        test_appointment_id,
        test_user_id
    ):
        """Test that rescheduling when clinic is open proceeds."""
        # Arrange
        test_appointment.status = "scheduled"
        mock_appointment_repo.get_appointment_by_id.return_value = test_appointment
        mock_pet_repo.get_by_id.return_value = test_pet
        
        # Mock clinic is open
        clinic_status = ClinicStatus(status="open", updated_at=datetime.utcnow())
        mock_clinic_status_repo.get_current_status.return_value = clinic_status
        
        # Mock time slot is available
        mock_appointment_repo.check_time_slot_available.return_value = True
        
        # Mock successful update
        updated_appointment = test_appointment
        mock_appointment_repo.update_appointment_times.return_value = updated_appointment
        
        new_start = datetime.utcnow() + timedelta(days=2)
        new_end = new_start + timedelta(hours=1)
        
        # Act
        result = appointment_service.reschedule_appointment(
            test_appointment_id,
            test_user_id,
            new_start,
            new_end
        )
        
        # Assert - should not raise exception
        assert result is not None


class TestTimeSlotAvailability:
    """Test that reschedule_appointment validates time slot availability.
    
    Requirements: 6.3
    """
    
    def test_reschedule_to_unavailable_slot_raises_bad_request(
        self,
        appointment_service,
        mock_appointment_repo,
        mock_pet_repo,
        mock_clinic_status_repo,
        test_appointment,
        test_pet,
        test_appointment_id,
        test_user_id
    ):
        """Test that rescheduling to unavailable slot raises BadRequestException."""
        # Arrange
        test_appointment.status = "scheduled"
        mock_appointment_repo.get_appointment_by_id.return_value = test_appointment
        mock_pet_repo.get_by_id.return_value = test_pet
        
        # Mock clinic is open
        clinic_status = ClinicStatus(status="open", updated_at=datetime.utcnow())
        mock_clinic_status_repo.get_current_status.return_value = clinic_status
        
        # Mock time slot is NOT available
        mock_appointment_repo.check_time_slot_available.return_value = False
        
        new_start = datetime.utcnow() + timedelta(days=2)
        new_end = new_start + timedelta(hours=1)
        
        # Act & Assert
        with pytest.raises(BadRequestException) as exc_info:
            appointment_service.reschedule_appointment(
                test_appointment_id,
                test_user_id,
                new_start,
                new_end
            )
        
        assert "The requested time slot is not available" in str(exc_info.value.detail)
    
    def test_reschedule_excludes_current_appointment_from_availability_check(
        self,
        appointment_service,
        mock_appointment_repo,
        mock_pet_repo,
        mock_clinic_status_repo,
        test_appointment,
        test_pet,
        test_appointment_id,
        test_user_id
    ):
        """Test that availability check excludes the current appointment being rescheduled."""
        # Arrange
        test_appointment.status = "scheduled"
        mock_appointment_repo.get_appointment_by_id.return_value = test_appointment
        mock_pet_repo.get_by_id.return_value = test_pet
        
        # Mock clinic is open
        clinic_status = ClinicStatus(status="open", updated_at=datetime.utcnow())
        mock_clinic_status_repo.get_current_status.return_value = clinic_status
        
        # Mock time slot is available
        mock_appointment_repo.check_time_slot_available.return_value = True
        
        # Mock successful update
        updated_appointment = test_appointment
        mock_appointment_repo.update_appointment_times.return_value = updated_appointment
        
        new_start = datetime.utcnow() + timedelta(days=2)
        new_end = new_start + timedelta(hours=1)
        
        # Act
        appointment_service.reschedule_appointment(
            test_appointment_id,
            test_user_id,
            new_start,
            new_end
        )
        
        # Assert - check that exclude_appointment_id was passed
        mock_appointment_repo.check_time_slot_available.assert_called_once_with(
            new_start,
            new_end,
            exclude_appointment_id=test_appointment_id
        )


class TestSuccessfulRescheduling:
    """Test successful appointment rescheduling.
    
    Requirements: 6.5, 6.7
    """
    
    def test_successful_reschedule_returns_updated_appointment(
        self,
        appointment_service,
        mock_appointment_repo,
        mock_pet_repo,
        mock_clinic_status_repo,
        test_appointment,
        test_pet,
        test_appointment_id,
        test_user_id
    ):
        """Test that successful reschedule returns the updated appointment."""
        # Arrange
        test_appointment.status = "scheduled"
        mock_appointment_repo.get_appointment_by_id.return_value = test_appointment
        mock_pet_repo.get_by_id.return_value = test_pet
        
        # Mock clinic is open
        clinic_status = ClinicStatus(status="open", updated_at=datetime.utcnow())
        mock_clinic_status_repo.get_current_status.return_value = clinic_status
        
        # Mock time slot is available
        mock_appointment_repo.check_time_slot_available.return_value = True
        
        # Mock successful update
        new_start = datetime.utcnow() + timedelta(days=2)
        new_end = new_start + timedelta(hours=1)
        updated_appointment = Appointment(
            id=test_appointment_id,
            pet_id=test_pet.id,
            user_id=test_user_id,
            start_time=new_start,
            end_time=new_end,
            service_type="routine",
            status="scheduled"
        )
        mock_appointment_repo.update_appointment_times.return_value = updated_appointment
        
        # Act
        result = appointment_service.reschedule_appointment(
            test_appointment_id,
            test_user_id,
            new_start,
            new_end
        )
        
        # Assert
        assert result is not None
        assert result.id == test_appointment_id
        assert result.start_time == new_start
        assert result.end_time == new_end
        mock_appointment_repo.update_appointment_times.assert_called_once_with(
            test_appointment_id,
            new_start,
            new_end
        )
    
    def test_successful_reschedule_calls_repository_update(
        self,
        appointment_service,
        mock_appointment_repo,
        mock_pet_repo,
        mock_clinic_status_repo,
        test_appointment,
        test_pet,
        test_appointment_id,
        test_user_id
    ):
        """Test that successful reschedule calls repository update_appointment_times."""
        # Arrange
        test_appointment.status = "confirmed"
        mock_appointment_repo.get_appointment_by_id.return_value = test_appointment
        mock_pet_repo.get_by_id.return_value = test_pet
        
        # Mock clinic is open
        clinic_status = ClinicStatus(status="open", updated_at=datetime.utcnow())
        mock_clinic_status_repo.get_current_status.return_value = clinic_status
        
        # Mock time slot is available
        mock_appointment_repo.check_time_slot_available.return_value = True
        
        # Mock successful update
        updated_appointment = test_appointment
        mock_appointment_repo.update_appointment_times.return_value = updated_appointment
        
        new_start = datetime.utcnow() + timedelta(days=3)
        new_end = new_start + timedelta(hours=2)
        
        # Act
        appointment_service.reschedule_appointment(
            test_appointment_id,
            test_user_id,
            new_start,
            new_end
        )
        
        # Assert
        mock_appointment_repo.update_appointment_times.assert_called_once_with(
            test_appointment_id,
            new_start,
            new_end
        )
