"""
Tests for AppointmentReschedule schema.

This module tests that the AppointmentReschedule schema:
- Requires both start_time and end_time fields
- Validates that end_time is after start_time
- Rejects invalid time ranges

Requirements: 6.2
"""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from app.features.appointments.schemas import AppointmentReschedule


class TestAppointmentRescheduleRequiredFields:
    """Test that both start_time and end_time are required."""
    
    def test_missing_start_time_rejected(self):
        """Test that reschedule request without start_time is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AppointmentReschedule(
                end_time=datetime(2024, 1, 15, 10, 0)
            )
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("start_time",)
        assert errors[0]["type"] == "missing"
    
    def test_missing_end_time_rejected(self):
        """Test that reschedule request without end_time is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AppointmentReschedule(
                start_time=datetime(2024, 1, 15, 10, 0)
            )
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("end_time",)
        assert errors[0]["type"] == "missing"
    
    def test_missing_both_fields_rejected(self):
        """Test that reschedule request without any fields is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AppointmentReschedule()
        
        errors = exc_info.value.errors()
        assert len(errors) == 2
        error_fields = {error["loc"][0] for error in errors}
        assert error_fields == {"start_time", "end_time"}


class TestEndTimeAfterStartTimeValidation:
    """Test end_time must be after start_time - Requirements 6.2."""
    
    def test_valid_time_range_accepted(self):
        """Test that valid time range with end_time after start_time is accepted."""
        start = datetime(2024, 1, 15, 10, 0)
        end = datetime(2024, 1, 15, 11, 0)
        
        reschedule = AppointmentReschedule(
            start_time=start,
            end_time=end
        )
        
        assert reschedule.start_time == start
        assert reschedule.end_time == end
    
    def test_one_hour_time_range_accepted(self):
        """Test that a 1-hour time range is accepted."""
        start = datetime(2024, 1, 15, 14, 30)
        end = datetime(2024, 1, 15, 15, 30)
        
        reschedule = AppointmentReschedule(
            start_time=start,
            end_time=end
        )
        
        assert reschedule.start_time == start
        assert reschedule.end_time == end
    
    def test_short_time_range_accepted(self):
        """Test that a short time range (15 minutes) is accepted."""
        start = datetime(2024, 1, 15, 9, 0)
        end = datetime(2024, 1, 15, 9, 15)
        
        reschedule = AppointmentReschedule(
            start_time=start,
            end_time=end
        )
        
        assert reschedule.start_time == start
        assert reschedule.end_time == end
    
    def test_long_time_range_accepted(self):
        """Test that a long time range (2 hours) is accepted."""
        start = datetime(2024, 1, 15, 8, 0)
        end = datetime(2024, 1, 15, 10, 0)
        
        reschedule = AppointmentReschedule(
            start_time=start,
            end_time=end
        )
        
        assert reschedule.start_time == start
        assert reschedule.end_time == end
    
    def test_end_time_equal_to_start_time_rejected(self):
        """Test that end_time equal to start_time is rejected."""
        same_time = datetime(2024, 1, 15, 10, 0)
        
        with pytest.raises(ValidationError) as exc_info:
            AppointmentReschedule(
                start_time=same_time,
                end_time=same_time
            )
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("end_time",)
        assert "end_time must be after start_time" in str(errors[0]["msg"])
    
    def test_end_time_before_start_time_rejected(self):
        """Test that end_time before start_time is rejected."""
        start = datetime(2024, 1, 15, 10, 0)
        end = datetime(2024, 1, 15, 9, 0)  # 1 hour before start
        
        with pytest.raises(ValidationError) as exc_info:
            AppointmentReschedule(
                start_time=start,
                end_time=end
            )
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("end_time",)
        assert "end_time must be after start_time" in str(errors[0]["msg"])
    
    def test_end_time_one_second_before_start_rejected(self):
        """Test that end_time even 1 second before start_time is rejected."""
        start = datetime(2024, 1, 15, 10, 0, 0)
        end = datetime(2024, 1, 15, 9, 59, 59)
        
        with pytest.raises(ValidationError) as exc_info:
            AppointmentReschedule(
                start_time=start,
                end_time=end
            )
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("end_time",)
    
    def test_end_time_one_second_after_start_accepted(self):
        """Test that end_time even 1 second after start_time is accepted."""
        start = datetime(2024, 1, 15, 10, 0, 0)
        end = datetime(2024, 1, 15, 10, 0, 1)
        
        reschedule = AppointmentReschedule(
            start_time=start,
            end_time=end
        )
        
        assert reschedule.start_time == start
        assert reschedule.end_time == end


class TestSchemaIntegration:
    """Test overall schema behavior and integration."""
    
    def test_schema_serialization(self):
        """Test that schema can be serialized to dict."""
        start = datetime(2024, 1, 15, 10, 0)
        end = datetime(2024, 1, 15, 11, 0)
        
        reschedule = AppointmentReschedule(
            start_time=start,
            end_time=end
        )
        
        data = reschedule.model_dump()
        assert isinstance(data, dict)
        assert data["start_time"] == start
        assert data["end_time"] == end
    
    def test_schema_json_serialization(self):
        """Test that schema can be serialized to JSON."""
        start = datetime(2024, 1, 15, 10, 0)
        end = datetime(2024, 1, 15, 11, 0)
        
        reschedule = AppointmentReschedule(
            start_time=start,
            end_time=end
        )
        
        json_str = reschedule.model_dump_json()
        assert isinstance(json_str, str)
        assert "2024-01-15T10:00:00" in json_str
        assert "2024-01-15T11:00:00" in json_str
    
    def test_schema_from_dict(self):
        """Test that schema can be created from dict."""
        data = {
            "start_time": datetime(2024, 1, 15, 10, 0),
            "end_time": datetime(2024, 1, 15, 11, 0)
        }
        
        reschedule = AppointmentReschedule(**data)
        assert reschedule.start_time == data["start_time"]
        assert reschedule.end_time == data["end_time"]
    
    def test_datetime_with_timezone_accepted(self):
        """Test that datetime objects with timezone info are accepted."""
        from datetime import timezone
        
        start = datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 15, 11, 0, tzinfo=timezone.utc)
        
        reschedule = AppointmentReschedule(
            start_time=start,
            end_time=end
        )
        
        assert reschedule.start_time == start
        assert reschedule.end_time == end
    
    def test_cross_day_time_range_accepted(self):
        """Test that time range spanning multiple days is accepted."""
        start = datetime(2024, 1, 15, 23, 0)
        end = datetime(2024, 1, 16, 1, 0)  # Next day
        
        reschedule = AppointmentReschedule(
            start_time=start,
            end_time=end
        )
        
        assert reschedule.start_time == start
        assert reschedule.end_time == end
