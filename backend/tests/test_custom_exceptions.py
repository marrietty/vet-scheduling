"""
Unit tests for custom exception classes.

Tests verify that each custom exception:
- Returns the correct HTTP status code
- Returns the expected error message
- Includes appropriate headers where needed
"""

import pytest
from fastapi import status

from app.common.exceptions import (
    NotFoundException,
    ForbiddenException,
    BadRequestException,
    UnauthorizedException,
    TokenBlacklistedException,
    ProfileUpdateForbiddenException,
    AppointmentRescheduleForbiddenException,
    TimeSlotUnavailableException,
)


class TestExistingExceptions:
    """Test existing exception classes to ensure they still work correctly."""

    def test_not_found_exception(self):
        """Test NotFoundException returns 404 with correct message."""
        exc = NotFoundException("Pet")
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.detail == "Pet not found"

    def test_forbidden_exception(self):
        """Test ForbiddenException returns 403 with correct message."""
        exc = ForbiddenException("Custom message")
        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.detail == "Custom message"

    def test_bad_request_exception(self):
        """Test BadRequestException returns 400 with correct message."""
        exc = BadRequestException("Invalid input")
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.detail == "Invalid input"

    def test_unauthorized_exception(self):
        """Test UnauthorizedException returns 401 with correct message and headers."""
        exc = UnauthorizedException("Invalid credentials")
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.detail == "Invalid credentials"
        assert exc.headers == {"WWW-Authenticate": "Bearer"}


class TestNewExceptions:
    """Test new exception classes added for vet clinic enhancements."""

    def test_token_blacklisted_exception_default_message(self):
        """Test TokenBlacklistedException returns 401 with default message."""
        exc = TokenBlacklistedException()
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.detail == "Token has been invalidated"
        assert exc.headers == {"WWW-Authenticate": "Bearer"}

    def test_token_blacklisted_exception_custom_message(self):
        """Test TokenBlacklistedException accepts custom message."""
        exc = TokenBlacklistedException("Custom token error")
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.detail == "Custom token error"
        assert exc.headers == {"WWW-Authenticate": "Bearer"}

    def test_profile_update_forbidden_exception_default_message(self):
        """Test ProfileUpdateForbiddenException returns 403 with default message."""
        exc = ProfileUpdateForbiddenException()
        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.detail == "Cannot access another user's profile"

    def test_profile_update_forbidden_exception_custom_message(self):
        """Test ProfileUpdateForbiddenException accepts custom message."""
        exc = ProfileUpdateForbiddenException("Custom profile error")
        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.detail == "Custom profile error"

    def test_appointment_reschedule_forbidden_exception_default_message(self):
        """Test AppointmentRescheduleForbiddenException returns 403 with default message."""
        exc = AppointmentRescheduleForbiddenException()
        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.detail == "You can only reschedule appointments for your own pets"

    def test_appointment_reschedule_forbidden_exception_custom_message(self):
        """Test AppointmentRescheduleForbiddenException accepts custom message."""
        exc = AppointmentRescheduleForbiddenException("Custom appointment error")
        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.detail == "Custom appointment error"

    def test_time_slot_unavailable_exception_default_message(self):
        """Test TimeSlotUnavailableException returns 409 with default message."""
        exc = TimeSlotUnavailableException()
        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.detail == "The requested time slot is not available"

    def test_time_slot_unavailable_exception_custom_message(self):
        """Test TimeSlotUnavailableException accepts custom message."""
        exc = TimeSlotUnavailableException("Custom time slot error")
        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.detail == "Custom time slot error"


class TestExceptionInheritance:
    """Test that all custom exceptions properly inherit from HTTPException."""

    def test_all_exceptions_are_http_exceptions(self):
        """Verify all custom exceptions inherit from HTTPException."""
        from fastapi import HTTPException

        exceptions = [
            NotFoundException("Test"),
            ForbiddenException("Test"),
            BadRequestException("Test"),
            UnauthorizedException("Test"),
            TokenBlacklistedException(),
            ProfileUpdateForbiddenException(),
            AppointmentRescheduleForbiddenException(),
            TimeSlotUnavailableException(),
        ]

        for exc in exceptions:
            assert isinstance(exc, HTTPException)
