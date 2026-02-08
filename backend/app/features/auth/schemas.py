"""
Authentication request/response schemas.

This module defines Pydantic schemas for authentication endpoints:
- RegisterRequest: User registration with email and password
- LoginRequest: User login with email and password
- TokenResponse: JWT token response after successful authentication
"""

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """
    Request schema for user registration.
    
    Attributes:
        full_name: Full name of the user
        email: Valid email address for the user account
        password: Password for the user account (8-64 characters, will be hashed before storage)
    """
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Full name of the user"
    )
    email: EmailStr
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=64,
        description="Password must be 8-64 characters long"
    )
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password meets requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v) > 64:
            raise ValueError('Password must be at most 64 characters long')
        return v


class LoginRequest(BaseModel):
    """
    Request schema for user login.
    
    Attributes:
        email: Email address of the user
        password: Password for authentication
    """
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    Response schema for successful authentication.
    
    Attributes:
        access_token: JWT access token for authenticated requests
        token_type: Type of token (always "bearer")
    """
    access_token: str
    token_type: str = "bearer"