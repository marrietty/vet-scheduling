"""Appointment service for business logic."""
from datetime import datetime, timezone
from typing import List, Optional
import uuid


from app.features.appointments.models import Appointment
from app.features.appointments.repository import AppointmentRepository
from app.features.pets.repository import PetRepository
from app.features.clinic.repository import ClinicStatusRepository
from app.features.users.models import User
from app.common.exceptions import (
    NotFoundException,
    ForbiddenException,
    BadRequestException
)
from app.common.utils import calculate_end_time


class AppointmentService:
    """Service for appointment business logic.
    
    This service implements all appointment-related business rules including:
    - Appointment creation with validation (pet exists, ownership, future time, clinic open, no overlaps)
    - Automatic end_time calculation based on service type
    - Status transition rules (pending -> confirmed/completed, cancellation rules)
    - Role-based access control for appointments
    
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.10, 5.11, 5.12, 6.1, 6.2, 6.3, 6.5, 6.6, 6.7, 6.10
    """
    
    def __init__(
        self,
        appointment_repo: AppointmentRepository,
        pet_repo: PetRepository,
        clinic_status_repo: ClinicStatusRepository
    ):
        """Initialize the service with required repositories.
        
        Args:
            appointment_repo: Repository for appointment database operations
            pet_repo: Repository for pet database operations
            clinic_status_repo: Repository for clinic status database operations
        """
        self.appointment_repo = appointment_repo
        self.pet_repo = pet_repo
        self.clinic_status_repo = clinic_status_repo
    
    def create_appointment(
        self,
        pet_id: uuid.UUID,
        start_time: datetime,
        service_type: str,
        current_user: User,
        notes: Optional[str] = None
    ) -> Appointment:
        """Create appointment with business rule validation.
        
        This method implements all appointment creation validation rules:
        1. Validates pet exists (Requirement 5.1)
        2. Validates pet ownership for pet owners (Requirement 5.2)
        3. Validates start time is in the future (Requirement 5.4)
        4. Calculates end time based on service type (Requirement 5.5)
        5. Checks clinic is not closed (Requirement 5.10)
        6. Checks for overlapping appointments (Requirement 5.11)
        7. Creates appointment with "pending" status (Requirement 5.12)
        
        Args:
            pet_id: UUID of the pet for the appointment
            start_time: When the appointment should start
            service_type: Type of service (vaccination, routine, surgery, emergency)
            current_user: The authenticated user creating the appointment
            notes: Optional notes about the appointment
            
        Returns:
            Created Appointment object
            
        Raises:
            NotFoundException: If pet doesn't exist
            ForbiddenException: If pet owner tries to book for another user's pet
            BadRequestException: If validation fails (past time, clinic closed, overlap)
            
        Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.10, 5.11, 5.12
        """
        # 1. Validate pet exists and ownership (Requirements 5.1, 5.2)
        pet = self.pet_repo.get_by_id(pet_id)
        if not pet:
            raise NotFoundException("Pet")
        
        # Pet owners can only book for their own pets (Requirement 5.2)
        # Admins can book for any pet (Requirement 5.3)
        if current_user.role == "pet_owner" and pet.owner_id != current_user.id:
            raise ForbiddenException("You can only book for your own pets")
        
        # 2. Validate time is in future (Requirement 5.4)
        if start_time <= datetime.now(timezone.utc):
            raise BadRequestException("Appointment time must be in the future")
        
        # 3. Calculate end time (Requirement 5.5)
        end_time = calculate_end_time(start_time, service_type)
        
        # 4. Check clinic is open (Requirement 5.10)
        clinic_status = self.clinic_status_repo.get_current_status()
        if clinic_status.status == "close":
            raise BadRequestException("Clinic is closed")
        
        # 5. Check for overlaps (Requirement 5.11)
        if self.appointment_repo.check_overlap(start_time, end_time):
            raise BadRequestException("Time slot is occupied")
        
        # 6. Create appointment with "pending" status (Requirement 5.12)
        appointment = Appointment(
            pet_id=pet_id,
            user_id=current_user.id,
            start_time=start_time,
            end_time=end_time,
            service_type=service_type,
            notes=notes,
            status="pending"
        )
        
        return self.appointment_repo.create(appointment)
    
    def get_appointments(
        self,
        current_user: User,
        status: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Appointment]:
        """Get appointments based on user role with optional filters.
        
        Admins can see all appointments, pet owners can only see appointments
        for their own pets.
        
        Args:
            current_user: The authenticated user requesting appointments
            status: Optional filter by appointment status
            from_date: Optional filter for appointments starting on or after this date
            to_date: Optional filter for appointments starting on or before this date
            
        Returns:
            List of Appointment objects matching the filters
            
        Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6
        """
        if current_user.role == "admin":
            return self.appointment_repo.get_all(status, from_date, to_date)
        else:
            return self.appointment_repo.get_by_owner_id(
                current_user.id, status, from_date, to_date
            )
    
    def update_appointment_status(
        self,
        appointment_id: uuid.UUID,
        new_status: str,
        current_user: User
    ) -> Appointment:
        """Update appointment status with validation.
        
        This method implements status transition rules:
        - Cannot change completed or cancelled appointments (Requirements 6.5, 6.6)
        - Only admin can confirm or complete appointments (Requirements 6.1, 6.2, 6.3, 6.4)
        - Pet owners can only cancel their own appointments (Requirements 6.7, 6.8)
        - Cannot cancel completed appointments (Requirement 6.10)
        
        Args:
            appointment_id: UUID of the appointment to update
            new_status: New status value (confirmed, completed, cancelled)
            current_user: The authenticated user updating the status
            
        Returns:
            Updated Appointment object
            
        Raises:
            NotFoundException: If appointment doesn't exist
            BadRequestException: If status transition is invalid
            ForbiddenException: If user lacks permission for the status change
            
        Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.10
        """
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Appointment")
        
        # Cannot change completed or cancelled appointments (Requirements 6.5, 6.6)
        if appointment.status in ["completed", "cancelled"]:
            raise BadRequestException(
                f"Cannot change status of {appointment.status} appointment"
            )
        
        # Only admin can confirm or complete (Requirements 6.1, 6.2, 6.3, 6.4)
        if new_status in ["confirmed", "completed"] and current_user.role != "admin":
            raise ForbiddenException("Only admin can confirm or complete appointments")
        
        # Pet owners can only cancel their own appointments (Requirements 6.7, 6.8)
        if new_status == "cancelled":
            if current_user.role == "pet_owner":
                pet = self.pet_repo.get_by_id(appointment.pet_id)
                if pet and pet.owner_id != current_user.id:
                    raise ForbiddenException("You can only cancel your own appointments")
        
        # Cannot cancel completed appointments (Requirement 6.10)
        if new_status == "cancelled" and appointment.status == "completed":
            raise BadRequestException("Cannot cancel completed appointment")
        
        appointment.status = new_status
        return self.appointment_repo.update(appointment)
    
    def cancel_appointment(
        self,
        appointment_id: uuid.UUID,
        current_user: User
    ) -> None:
        """Cancel appointment (delete from database).
        
        This method validates ownership and status before deleting:
        - Pet owners can only cancel their own appointments (Requirements 6.7, 6.8)
        - Admins can cancel any appointment (Requirement 6.9)
        - Cannot cancel completed appointments (Requirement 6.10)
        
        Args:
            appointment_id: UUID of the appointment to cancel
            current_user: The authenticated user cancelling the appointment
            
        Raises:
            NotFoundException: If appointment doesn't exist
            ForbiddenException: If pet owner tries to cancel another user's appointment
            BadRequestException: If trying to cancel a completed appointment
            
        Requirements: 6.7, 6.8, 6.9, 6.10
        """
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Appointment")
        
        # Validate ownership for pet owners (Requirements 6.7, 6.8)
        if current_user.role == "pet_owner":
            pet = self.pet_repo.get_by_id(appointment.pet_id)
            if pet and pet.owner_id != current_user.id:
                raise ForbiddenException("You can only cancel your own appointments")
        
        # Cannot cancel completed appointments (Requirement 6.10)
        if appointment.status == "completed":
            raise BadRequestException("Cannot cancel completed appointment")
        
        self.appointment_repo.delete(appointment)
