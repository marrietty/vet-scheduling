"""
Error response schemas for consistent API error formatting.

All error responses include:
- detail: Human-readable error message
- error_type: Machine-readable error classification
- timestamp: ISO 8601 timestamp when the error occurred

Requirements: 1.2, 2.4, 3.7, 3.8, 6.6, 6.9
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """
    Standard error response format for all API errors.
    
    This schema ensures consistent error responses across the API,
    making it easier for clients to handle errors programmatically.
    
    Attributes:
        detail: Human-readable error message describing what went wrong
        error_type: Machine-readable error classification (e.g., "token_blacklisted", "not_found")
        timestamp: ISO 8601 timestamp when the error occurred
    
    Example:
        {
            "detail": "Token has been invalidated",
            "error_type": "token_blacklisted",
            "timestamp": "2024-01-15T10:30:00.123456"
        }
    """
    
    detail: str = Field(..., description="Human-readable error message")
    error_type: str = Field(..., description="Machine-readable error classification")
    timestamp: str = Field(..., description="ISO 8601 timestamp when the error occurred")
    
    @classmethod
    def create(cls, detail: str, error_type: str) -> "ErrorResponse":
        """
        Create an error response with the current timestamp.
        
        Args:
            detail: Human-readable error message
            error_type: Machine-readable error classification
            
        Returns:
            ErrorResponse instance with current timestamp
        """
        return cls(
            detail=detail,
            error_type=error_type,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
