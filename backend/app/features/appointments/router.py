"""
Appointment router for API endpoints.

This module implements the HTTP endpoints for appointment management:
- POST /api/v1/appointments: Create a new appointment
- GET /api/v1/appointments: List appointments with filters (status, from_date, to_date)
- PATCH /api/v1/appointments/{appointment_id}/status: Update appointment status (admin only)
- PATCH /api/v1/appointments/{appointment_id}/reschedule: Reschedule an appointment
- DELETE /api/v1/appointments/{appointment_id}: Cancel/delete an appointment

All endpoints require authentication. Pet owners can only access appointments for
their own pets, while admins can access all appointments.

Requirements: 5.1, 6.1, 7.1, 7.3, 7.4, 7.5
"""

from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session
from typing import List, Optional
from datetime import datetime
import uuid

from app.core.database import get_session
from app.common.dependencies import get_current_user, require_role
from app.features.users.models import User
from app.features.appointments.schemas import (
    AppointmentCreateRequest,
    AppointmentUpdateStatusRequest,
    AppointmentReschedule,
    AppointmentResponse
)
from app.features.appointments.repository import AppointmentRepository
from app.features.appointments.service import AppointmentService
from app.features.pets.repository import PetRepository
from app.features.clinic.repository import ClinicStatusRepository
from datetime import date as date_type


router = APIRouter(prefix="/api/v1/appointments", tags=["Appointments"])


@router.get("/available-slots")
def get_available_slots(
    date: date_type = Query(..., description="Date to check for available slots (YYYY-MM-DD)"),
    service_type: str = Query("routine", description="Service type: vaccination, routine, surgery, or emergency"),
    session: Session = Depends(get_session)
):
    """
    Get available appointment time slots for a given date.
    
    Returns time slots within clinic operating hours (8:00 AM - 8:00 PM)
    that don't conflict with existing appointments. Slots are generated
    in 30-minute increments based on the service type duration.
    
    No authentication required — anyone can check availability.
    
    Args:
        date: Date to check (YYYY-MM-DD format)
        service_type: Type of service to determine slot duration
        session: Database session
        
    Returns:
        List of available time slots with start_time and end_time
    """
    appointment_repo = AppointmentRepository(session)
    pet_repo = PetRepository(session)
    clinic_status_repo = ClinicStatusRepository(session)
    
    appointment_service = AppointmentService(
        appointment_repo, pet_repo, clinic_status_repo
    )
    
    slots = appointment_service.get_available_slots(date, service_type)
    session.commit()
    return slots


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    request: AppointmentCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> AppointmentResponse:
    """
    Create a new appointment.
    
    The appointment is validated against business rules:
    - Pet must exist and be owned by the user (or user is admin)
    - Start time must be in the future
    - Clinic must not be closed
    - Time slot must not overlap with existing pending/confirmed appointments
    - End time is automatically calculated based on service type
    
    The created appointment has status "pending".
    
    Args:
        request: Appointment creation request data
        current_user: Authenticated user (from JWT token)
        session: Database session
        
    Returns:
        Created appointment
        
    Raises:
        401: If authentication fails
        403: If pet owner tries to book for another user's pet
        404: If pet doesn't exist
        400: If validation fails (past time, clinic closed, overlap)
        422: If request data is invalid
        
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.10, 5.11, 5.12
    """
    appointment_repo = AppointmentRepository(session)
    pet_repo = PetRepository(session)
    clinic_status_repo = ClinicStatusRepository(session)
    
    appointment_service = AppointmentService(
        appointment_repo, pet_repo, clinic_status_repo
    )
    
    appointment = appointment_service.create_appointment(
        pet_id=request.pet_id,
        start_time=request.start_time,
        service_type=request.service_type,
        notes=request.notes,
        current_user=current_user
    )
    
    session.commit()
    return AppointmentResponse.model_validate(appointment)


@router.get("", response_model=List[AppointmentResponse])
def get_appointments(
    status: Optional[str] = Query(None, description="Filter by appointment status"),
    from_date: Optional[datetime] = Query(None, description="Filter appointments starting on or after this date"),
    to_date: Optional[datetime] = Query(None, description="Filter appointments starting on or before this date"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> List[AppointmentResponse]:
    """
    Get appointments with optional filters.
    
    - Admin users: Returns all appointments in the system
    - Pet owners: Returns only appointments for pets owned by the authenticated user
    
    Supports filtering by:
    - status: Filter by appointment status (pending, confirmed, cancelled, completed)
    - from_date: Only appointments starting on or after this date
    - to_date: Only appointments starting on or before this date
    
    Multiple filters can be combined.
    
    Args:
        status: Optional status filter
        from_date: Optional start date filter
        to_date: Optional end date filter
        current_user: Authenticated user (from JWT token)
        session: Database session
        
    Returns:
        List of appointments matching the filters
        
    Raises:
        401: If authentication fails
        
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6
    """
    appointment_repo = AppointmentRepository(session)
    pet_repo = PetRepository(session)
    clinic_status_repo = ClinicStatusRepository(session)
    
    appointment_service = AppointmentService(
        appointment_repo, pet_repo, clinic_status_repo
    )
    
    appointments = appointment_service.get_appointments(
        current_user=current_user,
        status=status,
        from_date=from_date,
        to_date=to_date
    )
    
    return [AppointmentResponse.model_validate(apt) for apt in appointments]


@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
def update_appointment_status(
    appointment_id: uuid.UUID,
    request: AppointmentUpdateStatusRequest,
    current_user: User = Depends(require_role(["admin"])),
    session: Session = Depends(get_session)
) -> AppointmentResponse:
    """
    Update appointment status (admin only).
    
    This endpoint is restricted to admin users only. Admins can:
    - Confirm pending appointments (pending -> confirmed)
    - Complete confirmed appointments (confirmed -> completed)
    - Cancel appointments (any status -> cancelled, except completed)
    
    Status transition rules:
    - Cannot change status of completed appointments
    - Cannot change status of cancelled appointments
    - Cannot cancel completed appointments
    
    Args:
        appointment_id: UUID of the appointment to update
        request: Status update request data
        current_user: Authenticated admin user (from JWT token)
        session: Database session
        
    Returns:
        Updated appointment
        
    Raises:
        401: If authentication fails
        403: If user is not an admin
        404: If appointment doesn't exist
        400: If status transition is invalid
        422: If request data is invalid
        
    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6
    """
    appointment_repo = AppointmentRepository(session)
    pet_repo = PetRepository(session)
    clinic_status_repo = ClinicStatusRepository(session)
    
    appointment_service = AppointmentService(
        appointment_repo, pet_repo, clinic_status_repo
    )
    
    appointment = appointment_service.update_appointment_status(
        appointment_id=appointment_id,
        new_status=request.status,
        current_user=current_user
    )
    
    session.commit()
    return AppointmentResponse.model_validate(appointment)


@router.patch("/{appointment_id}/reschedule", response_model=AppointmentResponse)
def reschedule_appointment(
    appointment_id: uuid.UUID,
    reschedule_data: AppointmentReschedule,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> AppointmentResponse:
    """
    Reschedule an appointment to a new time slot.
    
    Allows pet owners to reschedule appointments for their own pets to a different date
    and time. The endpoint performs comprehensive validation to ensure the new time slot
    is valid, available, and within clinic operating hours. Only appointments in
    'scheduled' or 'confirmed' status can be rescheduled.
    
    **Process:**
    1. Authenticates the user via JWT token (get_current_user dependency)
    2. Validates the user owns the pet associated with the appointment
    3. Verifies the appointment status is 'scheduled' or 'confirmed'
    4. Validates the new time range (end_time must be after start_time)
    5. Checks that the clinic is open during the requested time
    6. Verifies the new time slot doesn't conflict with existing appointments
    7. Updates the appointment's start_time and end_time
    8. Updates the appointment's updated_at timestamp
    9. Returns the updated appointment
    
    **Parameters:**
    - **appointment_id** (path): UUID of the appointment to reschedule
    - **Authorization header**: Required. Must contain a valid Bearer token
      - Format: `Authorization: Bearer <token>`
    
    **Request Body:**
    ```json
    {
        "start_time": "2024-02-15T14:00:00Z",
        "end_time": "2024-02-15T15:00:00Z"
    }
    ```
    
    **Request Fields:**
    - **start_time** (required): New start time for the appointment
      - Must be a valid ISO 8601 datetime
      - Must be in the future
      - Must fall within clinic operating hours
    - **end_time** (required): New end time for the appointment
      - Must be a valid ISO 8601 datetime
      - Must be after start_time
      - Must fall within clinic operating hours
    
    **Response Format:**
    ```json
    {
        "id": "uuid-string",
        "pet_id": "uuid-string",
        "start_time": "2024-02-15T14:00:00Z",
        "end_time": "2024-02-15T15:00:00Z",
        "service_type": "checkup",
        "status": "scheduled",
        "notes": "Annual checkup",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-20T16:45:00Z"
    }
    ```
    
    **Error Responses:**
    - **401 Unauthorized**: 
      - Token is invalid, expired, or missing
      - Token has been blacklisted (user logged out)
      - Message: "Invalid or expired token" or "Token has been invalidated"
    - **403 Forbidden**: 
      - User doesn't own the pet associated with the appointment
      - Message: "You can only reschedule appointments for your own pets"
    - **404 Not Found**: 
      - Appointment with the given ID doesn't exist
      - Message: "Appointment not found"
    - **409 Conflict**: 
      - New time slot conflicts with an existing appointment (double booking)
      - Message: "The requested time slot is not available"
    - **422 Unprocessable Entity**: 
      - Validation fails for the request data
      - Messages:
        - "End time must be after start time"
        - "Clinic is closed during the requested time"
        - "Cannot reschedule completed or cancelled appointments"
        - "Appointment status must be 'scheduled' or 'confirmed'"
        - "Start time must be in the future"
    
    **Validation Rules:**
    - **Ownership**: User must own the pet associated with the appointment
    - **Status**: Appointment must be in 'scheduled' or 'confirmed' status
    - **Time Range**: end_time must be after start_time
    - **Clinic Hours**: Both start_time and end_time must fall within clinic operating hours
    - **Availability**: New time slot must not overlap with existing appointments
    - **Future Time**: start_time must be in the future
    
    **Example Usage:**
    ```bash
    curl -X PATCH "http://localhost:8000/api/v1/appointments/123e4567-e89b-12d3-a456-426614174000/reschedule" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
         -H "Content-Type: application/json" \
         -d '{
           "start_time": "2024-02-15T14:00:00Z",
           "end_time": "2024-02-15T15:00:00Z"
         }'
    ```
    
    **Requirements Satisfied:**
    - **Requirement 6.1**: Validate user owns the pet associated with the appointment
    - **Requirement 6.2**: Require both new start time and end time
    - **Requirement 6.3**: Validate new time slot does not conflict with existing appointments
    - **Requirement 6.4**: Check that clinic is open during the requested time
    - **Requirement 6.5**: Update appointment's start time and end time
    - **Requirement 6.6**: Reject reschedule requests that would create double booking
    - **Requirement 6.7**: Update appointment's updated_at timestamp
    - **Requirement 6.8**: Allow rescheduling only for appointments with status "scheduled" or "confirmed"
    - **Requirement 6.9**: Reject attempts to reschedule completed or cancelled appointments
    
    **Security Notes:**
    - Pet owners can only reschedule appointments for their own pets
    - Admin users can reschedule any appointment
    - All validation is performed before any database updates
    - The updated_at timestamp is automatically updated on successful reschedule
    
    **Business Rules:**
    - Completed appointments cannot be rescheduled
    - Cancelled appointments cannot be rescheduled
    - The new time slot must not create a double booking
    - The clinic must be open during the entire duration of the new time slot
    """
    appointment_repo = AppointmentRepository(session)
    pet_repo = PetRepository(session)
    clinic_status_repo = ClinicStatusRepository(session)
    
    appointment_service = AppointmentService(
        appointment_repo, pet_repo, clinic_status_repo
    )
    
    appointment = appointment_service.reschedule_appointment(
        appointment_id=appointment_id,
        user_id=current_user.id,
        new_start=reschedule_data.start_time,
        new_end=reschedule_data.end_time
    )
    
    session.commit()
    return AppointmentResponse.model_validate(appointment)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_appointment(
    appointment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> None:
    """
    Cancel/delete an appointment.
    
    - Admin users: Can cancel any appointment
    - Pet owners: Can only cancel appointments for their own pets
    
    Cannot cancel completed appointments.
    
    Args:
        appointment_id: UUID of the appointment to cancel
        current_user: Authenticated user (from JWT token)
        session: Database session
        
    Returns:
        No content (204 status code)
        
    Raises:
        401: If authentication fails
        403: If pet owner tries to cancel another user's appointment
        404: If appointment doesn't exist
        400: If trying to cancel a completed appointment
        
    Requirements: 6.7, 6.8, 6.9, 6.10
    """
    appointment_repo = AppointmentRepository(session)
    pet_repo = PetRepository(session)
    clinic_status_repo = ClinicStatusRepository(session)
    
    appointment_service = AppointmentService(
        appointment_repo, pet_repo, clinic_status_repo
    )
    
    appointment_service.cancel_appointment(appointment_id, current_user)
    
    session.commit()
