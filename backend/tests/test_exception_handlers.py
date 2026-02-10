"""
Unit tests for FastAPI exception handlers.

Tests verify that custom exceptions are properly handled with:
- Correct HTTP status codes
- Consistent error response format
- Timestamp and error_type fields included
- Appropriate error messages

Requirements: 1.2, 2.4, 3.7, 3.8, 6.6, 6.9
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.common.exceptions import (
    TokenBlacklistedException,
    ProfileUpdateForbiddenException,
    AppointmentRescheduleForbiddenException,
    TimeSlotUnavailableException
)


client = TestClient(app)


class TestTokenBlacklistedExceptionHandler:
    """Test exception handler for TokenBlacklistedException."""
    
    def test_token_blacklisted_returns_401(self):
        """
        Test that TokenBlacklistedException returns HTTP 401.
        
        Requirements: 1.2
        """
        # Create a test endpoint that raises TokenBlacklistedException
        @app.get("/test/token-blacklisted")
        def test_endpoint():
            raise TokenBlacklistedException()
        
        response = client.get("/test/token-blacklisted")
        
        assert response.status_code == 401
    
    def test_token_blacklisted_includes_error_type(self):
        """
        Test that error response includes error_type field.
        
        Requirements: 1.2
        """
        @app.get("/test/token-blacklisted-type")
        def test_endpoint():
            raise TokenBlacklistedException()
        
        response = client.get("/test/token-blacklisted-type")
        data = response.json()
        
        assert "error_type" in data
        assert data["error_type"] == "token_blacklisted"
    
    def test_token_blacklisted_includes_timestamp(self):
        """
        Test that error response includes timestamp field.
        
        Requirements: 1.2
        """
        @app.get("/test/token-blacklisted-timestamp")
        def test_endpoint():
            raise TokenBlacklistedException()
        
        response = client.get("/test/token-blacklisted-timestamp")
        data = response.json()
        
        assert "timestamp" in data
        # Verify timestamp is valid ISO format
        datetime.fromisoformat(data["timestamp"])
    
    def test_token_blacklisted_includes_detail(self):
        """
        Test that error response includes detail message.
        
        Requirements: 1.2
        """
        @app.get("/test/token-blacklisted-detail")
        def test_endpoint():
            raise TokenBlacklistedException()
        
        response = client.get("/test/token-blacklisted-detail")
        data = response.json()
        
        assert "detail" in data
        assert data["detail"] == "Token has been invalidated"
    
    def test_token_blacklisted_custom_message(self):
        """
        Test that custom error message is preserved.
        
        Requirements: 1.2
        """
        @app.get("/test/token-blacklisted-custom")
        def test_endpoint():
            raise TokenBlacklistedException("Custom blacklist message")
        
        response = client.get("/test/token-blacklisted-custom")
        data = response.json()
        
        assert data["detail"] == "Custom blacklist message"


class TestProfileUpdateForbiddenExceptionHandler:
    """Test exception handler for ProfileUpdateForbiddenException."""
    
    def test_profile_update_forbidden_returns_403(self):
        """
        Test that ProfileUpdateForbiddenException returns HTTP 403.
        
        Requirements: 3.7
        """
        @app.get("/test/profile-forbidden")
        def test_endpoint():
            raise ProfileUpdateForbiddenException()
        
        response = client.get("/test/profile-forbidden")
        
        assert response.status_code == 403
    
    def test_profile_update_forbidden_includes_error_type(self):
        """
        Test that error response includes error_type field.
        
        Requirements: 3.7
        """
        @app.get("/test/profile-forbidden-type")
        def test_endpoint():
            raise ProfileUpdateForbiddenException()
        
        response = client.get("/test/profile-forbidden-type")
        data = response.json()
        
        assert "error_type" in data
        assert data["error_type"] == "profile_update_forbidden"
    
    def test_profile_update_forbidden_includes_timestamp(self):
        """
        Test that error response includes timestamp field.
        
        Requirements: 3.7
        """
        @app.get("/test/profile-forbidden-timestamp")
        def test_endpoint():
            raise ProfileUpdateForbiddenException()
        
        response = client.get("/test/profile-forbidden-timestamp")
        data = response.json()
        
        assert "timestamp" in data
        # Verify timestamp is valid ISO format
        datetime.fromisoformat(data["timestamp"])
    
    def test_profile_update_forbidden_includes_detail(self):
        """
        Test that error response includes detail message.
        
        Requirements: 3.7
        """
        @app.get("/test/profile-forbidden-detail")
        def test_endpoint():
            raise ProfileUpdateForbiddenException()
        
        response = client.get("/test/profile-forbidden-detail")
        data = response.json()
        
        assert "detail" in data
        assert data["detail"] == "Cannot access another user's profile"


class TestAppointmentRescheduleForbiddenExceptionHandler:
    """Test exception handler for AppointmentRescheduleForbiddenException."""
    
    def test_appointment_reschedule_forbidden_returns_403(self):
        """
        Test that AppointmentRescheduleForbiddenException returns HTTP 403.
        
        Requirements: 6.6
        """
        @app.get("/test/appointment-forbidden")
        def test_endpoint():
            raise AppointmentRescheduleForbiddenException()
        
        response = client.get("/test/appointment-forbidden")
        
        assert response.status_code == 403
    
    def test_appointment_reschedule_forbidden_includes_error_type(self):
        """
        Test that error response includes error_type field.
        
        Requirements: 6.6
        """
        @app.get("/test/appointment-forbidden-type")
        def test_endpoint():
            raise AppointmentRescheduleForbiddenException()
        
        response = client.get("/test/appointment-forbidden-type")
        data = response.json()
        
        assert "error_type" in data
        assert data["error_type"] == "appointment_reschedule_forbidden"
    
    def test_appointment_reschedule_forbidden_includes_timestamp(self):
        """
        Test that error response includes timestamp field.
        
        Requirements: 6.6
        """
        @app.get("/test/appointment-forbidden-timestamp")
        def test_endpoint():
            raise AppointmentRescheduleForbiddenException()
        
        response = client.get("/test/appointment-forbidden-timestamp")
        data = response.json()
        
        assert "timestamp" in data
        # Verify timestamp is valid ISO format
        datetime.fromisoformat(data["timestamp"])
    
    def test_appointment_reschedule_forbidden_includes_detail(self):
        """
        Test that error response includes detail message.
        
        Requirements: 6.6
        """
        @app.get("/test/appointment-forbidden-detail")
        def test_endpoint():
            raise AppointmentRescheduleForbiddenException()
        
        response = client.get("/test/appointment-forbidden-detail")
        data = response.json()
        
        assert "detail" in data
        assert data["detail"] == "You can only reschedule appointments for your own pets"


class TestTimeSlotUnavailableExceptionHandler:
    """Test exception handler for TimeSlotUnavailableException."""
    
    def test_time_slot_unavailable_returns_409(self):
        """
        Test that TimeSlotUnavailableException returns HTTP 409.
        
        Requirements: 6.9
        """
        @app.get("/test/time-slot-unavailable")
        def test_endpoint():
            raise TimeSlotUnavailableException()
        
        response = client.get("/test/time-slot-unavailable")
        
        assert response.status_code == 409
    
    def test_time_slot_unavailable_includes_error_type(self):
        """
        Test that error response includes error_type field.
        
        Requirements: 6.9
        """
        @app.get("/test/time-slot-unavailable-type")
        def test_endpoint():
            raise TimeSlotUnavailableException()
        
        response = client.get("/test/time-slot-unavailable-type")
        data = response.json()
        
        assert "error_type" in data
        assert data["error_type"] == "time_slot_unavailable"
    
    def test_time_slot_unavailable_includes_timestamp(self):
        """
        Test that error response includes timestamp field.
        
        Requirements: 6.9
        """
        @app.get("/test/time-slot-unavailable-timestamp")
        def test_endpoint():
            raise TimeSlotUnavailableException()
        
        response = client.get("/test/time-slot-unavailable-timestamp")
        data = response.json()
        
        assert "timestamp" in data
        # Verify timestamp is valid ISO format
        datetime.fromisoformat(data["timestamp"])
    
    def test_time_slot_unavailable_includes_detail(self):
        """
        Test that error response includes detail message.
        
        Requirements: 6.9
        """
        @app.get("/test/time-slot-unavailable-detail")
        def test_endpoint():
            raise TimeSlotUnavailableException()
        
        response = client.get("/test/time-slot-unavailable-detail")
        data = response.json()
        
        assert "detail" in data
        assert data["detail"] == "The requested time slot is not available"


class TestErrorResponseFormat:
    """Test that all error responses follow consistent format."""
    
    def test_all_handlers_return_consistent_format(self):
        """
        Test that all exception handlers return the same response structure.
        
        All error responses should have: detail, error_type, timestamp
        
        Requirements: 1.2, 3.7, 6.6, 6.9
        """
        exceptions_to_test = [
            (TokenBlacklistedException, "/test/format-token"),
            (ProfileUpdateForbiddenException, "/test/format-profile"),
            (AppointmentRescheduleForbiddenException, "/test/format-appointment"),
            (TimeSlotUnavailableException, "/test/format-timeslot")
        ]
        
        for exception_class, path in exceptions_to_test:
            # Create test endpoint
            @app.get(path)
            def test_endpoint():
                raise exception_class()
            
            response = client.get(path)
            data = response.json()
            
            # Verify all required fields are present
            assert "detail" in data, f"{exception_class.__name__} missing 'detail'"
            assert "error_type" in data, f"{exception_class.__name__} missing 'error_type'"
            assert "timestamp" in data, f"{exception_class.__name__} missing 'timestamp'"
            
            # Verify no extra fields
            assert set(data.keys()) == {"detail", "error_type", "timestamp"}
