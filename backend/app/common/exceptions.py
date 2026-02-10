"""
Custom HTTP exceptions for the Vet Clinic Scheduling System.

These exceptions provide consistent error responses across the API:
- NotFoundException (404): Resource not found
- ForbiddenException (403): Access denied / insufficient permissions
- BadRequestException (400): Invalid request data or business rule violation
- UnauthorizedException (401): Authentication failure
- TokenBlacklistedException (401): Blacklisted token used for authentication
- ProfileUpdateForbiddenException (403): Cross-user profile update attempt
- AppointmentRescheduleForbiddenException (403): Appointment ownership violation
- TimeSlotUnavailableException (409): Double booking / time slot conflict
"""

from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """
    Raised when a requested resource doesn't exist.
    
    Returns HTTP 404 status code.
    
    Args:
        resource: The name of the resource that was not found (e.g., "Pet", "Appointment")
    
    Example:
        raise NotFoundException("Pet")
        # Returns: {"detail": "Pet not found"}
    """
    
    def __init__(self, resource: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found"
        )


class ForbiddenException(HTTPException):
    """
    Raised when user lacks permission for an action.
    
    Returns HTTP 403 status code.
    
    Args:
        message: Description of why access was denied
    
    Example:
        raise ForbiddenException("You can only access your own pets")
        # Returns: {"detail": "You can only access your own pets"}
    """
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )


class BadRequestException(HTTPException):
    """
    Raised when request data is invalid or violates business rules.
    
    Returns HTTP 400 status code.
    
    Args:
        message: Description of what is invalid about the request
    
    Example:
        raise BadRequestException("Start time must be in the future")
        # Returns: {"detail": "Start time must be in the future"}
    """
    
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


class UnauthorizedException(HTTPException):
    """
    Raised when authentication fails.
    
    Returns HTTP 401 status code with WWW-Authenticate header.
    
    Args:
        message: Description of the authentication failure
    
    Example:
        raise UnauthorizedException("Invalid credentials")
        # Returns: {"detail": "Invalid credentials"}
    """
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"}
        )


class TokenBlacklistedException(HTTPException):
    """
    Raised when a blacklisted token is used for authentication.
    
    Returns HTTP 401 status code with WWW-Authenticate header.
    
    This exception is thrown when a user attempts to use a token that has been
    invalidated through logout or other security measures.
    
    Example:
        raise TokenBlacklistedException()
        # Returns: {"detail": "Token has been invalidated"}
    """
    
    def __init__(self, message: str = "Token has been invalidated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ProfileUpdateForbiddenException(HTTPException):
    """
    Raised when a user attempts to update another user's profile.
    
    Returns HTTP 403 status code.
    
    This exception enforces the security rule that users can only modify
    their own profile information.
    
    Example:
        raise ProfileUpdateForbiddenException()
        # Returns: {"detail": "Cannot access another user's profile"}
    """
    
    def __init__(self, message: str = "Cannot access another user's profile"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )


class AppointmentRescheduleForbiddenException(HTTPException):
    """
    Raised when a user attempts to reschedule an appointment they don't own.
    
    Returns HTTP 403 status code.
    
    This exception enforces the business rule that users can only reschedule
    appointments for their own pets.
    
    Example:
        raise AppointmentRescheduleForbiddenException()
        # Returns: {"detail": "You can only reschedule appointments for your own pets"}
    """
    
    def __init__(self, message: str = "You can only reschedule appointments for your own pets"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )


class TimeSlotUnavailableException(HTTPException):
    """
    Raised when attempting to schedule or reschedule to an unavailable time slot.
    
    Returns HTTP 409 status code (Conflict).
    
    This exception is thrown when a requested time slot conflicts with an existing
    appointment, preventing double bookings.
    
    Example:
        raise TimeSlotUnavailableException()
        # Returns: {"detail": "The requested time slot is not available"}
    """
    
    def __init__(self, message: str = "The requested time slot is not available"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=message
        )
