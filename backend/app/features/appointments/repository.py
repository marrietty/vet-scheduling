"""Appointment repository for database operations."""
from sqlmodel import Session, select, and_
from typing import Optional, List
from datetime import datetime
import uuid

from app.features.appointments.models import Appointment
from app.features.pets.models import Pet


class AppointmentRepository:
    """Repository for Appointment database operations.
    
    This class handles all database queries related to appointments,
    following the repository pattern to abstract data access.
    """
    
    def __init__(self, session: Session):
        """Initialize the repository with a database session.
        
        Args:
            session: SQLModel database session
        """
        self.session = session
    
    def get_by_id(self, appointment_id: uuid.UUID) -> Optional[Appointment]:
        """Get appointment by ID.
        
        Args:
            appointment_id: UUID of the appointment to retrieve
            
        Returns:
            Appointment object if found, None otherwise
        """
        return self.session.get(Appointment, appointment_id)
    
    def get_all(
        self,
        status: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Appointment]:
        """Get all appointments with optional filters.
        
        Args:
            status: Optional status filter (pending, confirmed, cancelled, completed)
            from_date: Optional filter for appointments starting on or after this date
            to_date: Optional filter for appointments starting on or before this date
            
        Returns:
            List of Appointment objects matching the filters
        """
        statement = select(Appointment)
        
        if status:
            statement = statement.where(Appointment.status == status)
        if from_date:
            statement = statement.where(Appointment.start_time >= from_date)
        if to_date:
            statement = statement.where(Appointment.start_time <= to_date)
        
        return list(self.session.exec(statement).all())
    
    def get_by_owner_id(
        self,
        owner_id: uuid.UUID,
        status: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Appointment]:
        """Get appointments for pets owned by a specific user.
        
        This method joins with the Pet table to filter appointments
        by the pet's owner_id.
        
        Args:
            owner_id: UUID of the pet owner
            status: Optional status filter (pending, confirmed, cancelled, completed)
            from_date: Optional filter for appointments starting on or after this date
            to_date: Optional filter for appointments starting on or before this date
            
        Returns:
            List of Appointment objects for pets owned by the user
        """
        statement = select(Appointment).join(Pet).where(Pet.owner_id == owner_id)
        
        if status:
            statement = statement.where(Appointment.status == status)
        if from_date:
            statement = statement.where(Appointment.start_time >= from_date)
        if to_date:
            statement = statement.where(Appointment.start_time <= to_date)
        
        return list(self.session.exec(statement).all())
    
    def check_overlap(
        self,
        start_time: datetime,
        end_time: datetime,
        exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Check if time slot has overlapping pending/confirmed appointments.
        
        Two appointments overlap if:
        - One starts before the other ends AND
        - One ends after the other starts
        
        Only considers appointments with status "pending" or "confirmed".
        Cancelled and completed appointments are ignored.
        
        Args:
            start_time: Start time of the time slot to check
            end_time: End time of the time slot to check
            exclude_id: Optional appointment ID to exclude from the check
                       (useful when updating an existing appointment)
            
        Returns:
            True if there is an overlapping appointment, False otherwise
        """
        statement = select(Appointment).where(
            and_(
                Appointment.status.in_(["pending", "confirmed"]),
                Appointment.start_time < end_time,
                Appointment.end_time > start_time
            )
        )
        
        if exclude_id:
            statement = statement.where(Appointment.id != exclude_id)
        
        result = self.session.exec(statement).first()
        return result is not None
    
    def get_appointments_for_day(
        self,
        day_start: datetime,
        day_end: datetime
    ) -> List[Appointment]:
        """Get all active appointments (pending/confirmed) for a given day.
        
        Used to efficiently check slot availability by fetching all
        appointments in one query instead of per-slot queries.
        
        Args:
            day_start: Start of the day (inclusive)
            day_end: End of the day (exclusive)
            
        Returns:
            List of active Appointment objects for the day
        """
        statement = select(Appointment).where(
            and_(
                Appointment.status.in_(["pending", "confirmed"]),
                Appointment.start_time < day_end,
                Appointment.end_time > day_start
            )
        )
        return list(self.session.exec(statement).all())
    
    def create(self, appointment: Appointment) -> Appointment:
        """Create a new appointment in the database.
        
        Args:
            appointment: Appointment object to create
            
        Returns:
            Created Appointment object with database-generated fields populated
        """
        self.session.add(appointment)
        self.session.flush()
        self.session.refresh(appointment)
        return appointment
    
    def update(self, appointment: Appointment) -> Appointment:
        """Update an existing appointment in the database.
        
        Args:
            appointment: Appointment object with updated fields
            
        Returns:
            Updated Appointment object
        """
        appointment.updated_at = datetime.utcnow()
        self.session.add(appointment)
        self.session.flush()
        self.session.refresh(appointment)
        return appointment
    
    def delete(self, appointment: Appointment) -> None:
        """Delete an appointment from the database.
        
        Args:
            appointment: Appointment object to delete
        """
        self.session.delete(appointment)
        self.session.flush()
    
    def get_appointment_by_id(self, appointment_id: uuid.UUID) -> Optional[Appointment]:
        """Get appointment by ID for rescheduling operations.
        
        This is an alias for get_by_id() to match the design document naming.
        
        Args:
            appointment_id: UUID of the appointment to retrieve
            
        Returns:
            Appointment object if found, None otherwise
        """
        return self.get_by_id(appointment_id)
    
    def check_time_slot_available(
        self,
        start_time: datetime,
        end_time: datetime,
        exclude_appointment_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Check if a time slot is available for scheduling/rescheduling.
        
        This method checks for overlapping appointments, excluding the current
        appointment being rescheduled if provided. Returns True if the slot
        is available (no overlaps), False if there are conflicts.
        
        Args:
            start_time: Start time of the time slot to check
            end_time: End time of the time slot to check
            exclude_appointment_id: Optional appointment ID to exclude from the check
                                   (used when rescheduling an existing appointment)
            
        Returns:
            True if the time slot is available (no overlaps), False otherwise
        """
        # check_overlap returns True if there IS an overlap
        # We want to return True if the slot is AVAILABLE (no overlap)
        has_overlap = self.check_overlap(start_time, end_time, exclude_appointment_id)
        return not has_overlap
    
    def update_appointment_times(
        self,
        appointment_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime
    ) -> Appointment:
        """Update appointment start and end times for rescheduling.
        
        This method updates the appointment's start_time and end_time fields
        and automatically updates the updated_at timestamp.
        
        Args:
            appointment_id: UUID of the appointment to update
            start_time: New start time for the appointment
            end_time: New end time for the appointment
            
        Returns:
            Updated Appointment object
            
        Raises:
            ValueError: If appointment is not found
        """
        appointment = self.get_by_id(appointment_id)
        if not appointment:
            raise ValueError(f"Appointment with id {appointment_id} not found")
        
        appointment.start_time = start_time
        appointment.end_time = end_time
        appointment.updated_at = datetime.utcnow()
        
        self.session.add(appointment)
        self.session.flush()
        self.session.refresh(appointment)
        
        return appointment
