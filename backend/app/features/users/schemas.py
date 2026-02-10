"""
User profile request/response schemas.

This module defines Pydantic schemas for user profile endpoints:
- UserProfileResponse: Complete user profile information for API responses
- UserProfileUpdate: Request schema for updating user profile with validation
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


class UserProfileResponse(BaseModel):
    """
    Response schema for user profile information.
    
    This schema includes all non-sensitive user information for API responses.
    Sensitive fields like hashed_password are explicitly excluded.
    
    Attributes:
        id: Unique identifier for the user
        full_name: User's full name
        email: User's email address
        phone: User's phone number (optional)
        city: User's city location (optional)
        role: User role (admin or pet_owner)
        is_active: Whether the user account is active
        preferences: User preferences stored as JSON (optional)
        created_at: Timestamp when the user was created
    """
    model_config = ConfigDict(from_attributes=True)  # Allows creation from ORM models
    
    id: uuid.UUID = Field(description="Unique identifier for the user")
    full_name: str = Field(description="User's full name")
    email: str = Field(description="User's email address")
    phone: Optional[str] = Field(default=None, description="User's phone number")
    city: Optional[str] = Field(default=None, description="User's city location")
    role: str = Field(description="User role (admin or pet_owner)")
    is_active: bool = Field(description="Whether the user account is active")
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="User preferences")
    created_at: datetime = Field(description="Timestamp when the user was created")


class UserProfileUpdate(BaseModel):
    """
    Request schema for updating user profile information.
    
    All fields are optional, allowing users to update any subset of their profile.
    When a field is provided, it must pass validation rules.
    
    Attributes:
        full_name: User's full name (must not be empty if provided)
        email: User's email address (must be valid format if provided)
        phone: User's phone number (must be valid format if provided)
        city: User's city location (must not be empty if provided)
        preferences: User preferences stored as JSON
    """
    full_name: Optional[str] = Field(default=None, description="User's full name")
    email: Optional[str] = Field(default=None, description="User's email address")
    phone: Optional[str] = Field(default=None, description="User's phone number")
    city: Optional[str] = Field(default=None, description="User's city location")
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="User preferences")
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate that full_name is not empty when provided.
        
        Requirements: 3.1 - Name must not be empty
        """
        if v is not None:
            # Strip whitespace and check if empty
            if not v.strip():
                raise ValueError('Full name cannot be empty or whitespace only')
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate email format when provided.
        
        Requirements: 3.2 - Email must be valid format
        """
        if v is not None:
            # Basic email format validation
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Invalid email format')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate phone format when provided.
        
        Requirements: 3.3 - Phone must be valid format
        Accepts various formats: +1234567890, (123) 456-7890, 123-456-7890, etc.
        """
        if v is not None:
            # Remove common phone number formatting characters
            import re
            digits_only = re.sub(r'[^\d]', '', v)
            # Check if we have a reasonable number of digits (10-15 is typical for international)
            if len(digits_only) < 10 or len(digits_only) > 15:
                raise ValueError('Phone number must contain 10-15 digits')
        return v
    
    @field_validator('city')
    @classmethod
    def validate_city(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate that city is not empty when provided.
        
        Requirements: 4.4 - City must be non-empty when provided
        """
        if v is not None:
            # Strip whitespace and check if empty
            if not v.strip():
                raise ValueError('City cannot be empty or whitespace only')
        return v
