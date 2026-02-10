"""
User router for profile management endpoints.

This module provides HTTP endpoints for:
- GET /api/v1/users/profile: Get current user's profile information
- PATCH /api/v1/users/profile: Update current user's profile information
"""

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.database import get_session
from app.features.users.schemas import UserProfileResponse, UserProfileUpdate
from app.features.users.service import UserService
from app.features.users.repository import UserRepository
from app.common.dependencies import get_current_user
from app.features.users.models import User

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/profile", response_model=UserProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> UserProfileResponse:
    """
    Get current user's profile information.
    
    Retrieves the complete profile information for the currently authenticated user,
    excluding sensitive security information like password hashes. This endpoint
    returns all user-facing profile data including personal details, contact information,
    role, and preferences.
    
    **Process:**
    1. Authenticates the user via JWT token (get_current_user dependency)
    2. Retrieves the user's complete profile from the database
    3. Filters out sensitive fields (hashed_password, etc.)
    4. Returns all non-sensitive profile information
    
    **Parameters:**
    - **Authorization header**: Required. Must contain a valid Bearer token
      - Format: `Authorization: Bearer <token>`
    
    **Request Body:** None
    
    **Response Format:**
    ```json
    {
        "id": "uuid-string",
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-0123",
        "city": "San Francisco",
        "role": "pet_owner",
        "is_active": true,
        "preferences": {
            "notifications": true,
            "theme": "light"
        },
        "created_at": "2024-01-15T10:30:00Z"
    }
    ```
    
    **Response Fields:**
    - **id**: Unique user identifier (UUID)
    - **full_name**: User's full name
    - **email**: User's email address
    - **phone**: User's phone number (optional, may be null)
    - **city**: User's city location (optional, may be null)
    - **role**: User's role in the system (e.g., "pet_owner", "admin")
    - **is_active**: Whether the user account is active
    - **preferences**: User preferences as JSON object (optional, may be null or empty)
    - **created_at**: Account creation timestamp
    
    **Error Responses:**
    - **401 Unauthorized**: 
      - Token is invalid, expired, or missing
      - Token has been blacklisted (user logged out)
      - Message: "Invalid or expired token" or "Token has been invalidated"
    - **403 Forbidden**: 
      - User account has been deactivated
      - Message: "User account is deactivated"
    - **404 Not Found**: 
      - User record not found in database (rare edge case)
      - Message: "User not found"
    
    **Example Usage:**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/users/profile" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```
    
    **Requirements Satisfied:**
    - **Requirement 2.1**: Return user's full name, email, phone, city, role, and account status
    - **Requirement 2.2**: Do not return hashed password or other sensitive security information
    - **Requirement 2.3**: Require valid authentication to access profile information
    - **Requirement 2.4**: Return unauthorized error for unauthenticated requests
    - **Requirement 4.3**: Include city field in profile display if present
    - **Requirement 8.3**: Include current preferences when user retrieves profile
    
    **Security Notes:**
    - Only the authenticated user can view their own profile
    - Sensitive fields like password hashes are never included in the response
    - Token must be valid and not blacklisted
    """
    # Initialize repository and service
    user_repo = UserRepository(session)
    user_service = UserService(user_repo)
    
    # Get user profile (excludes sensitive fields)
    profile = user_service.get_current_user_profile(current_user.id)
    
    return profile


@router.patch("/profile", response_model=UserProfileResponse)
def update_profile(
    updates: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> UserProfileResponse:
    """
    Update current user's profile information.
    
    Allows the authenticated user to update their profile information including personal
    details, contact information, and preferences. All fields are optional - only the
    fields provided in the request will be updated. The endpoint performs comprehensive
    validation to ensure data integrity and uniqueness constraints.
    
    **Process:**
    1. Authenticates the user via JWT token (get_current_user dependency)
    2. Validates all provided updates according to business rules
    3. Checks email uniqueness if email is being updated
    4. Validates phone format if phone is being updated
    5. Validates city format if city is being updated
    6. Updates only the provided fields in the database
    7. Returns the complete updated profile information
    
    **Parameters:**
    - **Authorization header**: Required. Must contain a valid Bearer token
      - Format: `Authorization: Bearer <token>`
    
    **Request Body:** (All fields optional)
    ```json
    {
        "full_name": "Jane Smith",
        "email": "jane.smith@example.com",
        "phone": "+1-555-9876",
        "city": "Los Angeles",
        "preferences": {
            "notifications": false,
            "theme": "dark",
            "language": "en"
        }
    }
    ```
    
    **Request Fields:**
    - **full_name** (optional): User's full name
      - Must not be empty or whitespace-only
      - Validation: Non-empty string after trimming
    - **email** (optional): User's email address
      - Must be valid email format (contains @, valid domain)
      - Must not be already used by another user
      - Validation: Email format + uniqueness check
    - **phone** (optional): User's phone number
      - Must match valid phone format
      - Validation: Phone number pattern
    - **city** (optional): User's city location
      - Must not be empty or whitespace-only if provided
      - Validation: Non-empty string after trimming
    - **preferences** (optional): User preferences as JSON object
      - Must be valid JSON structure
      - Can contain any key-value pairs
      - Validation: Valid JSON object structure
    
    **Response Format:**
    ```json
    {
        "id": "uuid-string",
        "full_name": "Jane Smith",
        "email": "jane.smith@example.com",
        "phone": "+1-555-9876",
        "city": "Los Angeles",
        "role": "pet_owner",
        "is_active": true,
        "preferences": {
            "notifications": false,
            "theme": "dark",
            "language": "en"
        },
        "created_at": "2024-01-15T10:30:00Z"
    }
    ```
    
    **Error Responses:**
    - **401 Unauthorized**: 
      - Token is invalid, expired, or missing
      - Token has been blacklisted (user logged out)
      - Message: "Invalid or expired token" or "Token has been invalidated"
    - **403 Forbidden**: 
      - User account has been deactivated
      - Message: "User account is deactivated"
    - **404 Not Found**: 
      - User record not found in database
      - Message: "User not found"
    - **409 Conflict**: 
      - Email is already used by another user
      - Message: "Email already in use"
    - **422 Unprocessable Entity**: 
      - Validation fails for any field
      - Messages:
        - "Full name cannot be empty"
        - "Invalid email format"
        - "Invalid phone number format"
        - "City cannot be empty"
        - "Invalid preferences structure"
    
    **Example Usage:**
    ```bash
    # Update multiple fields
    curl -X PATCH "http://localhost:8000/api/v1/users/profile" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
         -H "Content-Type: application/json" \
         -d '{
           "full_name": "Jane Smith",
           "city": "Los Angeles",
           "preferences": {"notifications": false}
         }'
    
    # Update only preferences
    curl -X PATCH "http://localhost:8000/api/v1/users/profile" \
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
         -H "Content-Type: application/json" \
         -d '{"preferences": {"theme": "dark"}}'
    ```
    
    **Requirements Satisfied:**
    - **Requirement 3.1**: Validate name is not empty and update user record
    - **Requirement 3.2**: Validate email format and ensure not already used by another user
    - **Requirement 3.3**: Validate phone format and update user record
    - **Requirement 3.4**: Update city field in user record
    - **Requirement 3.5**: Store preferences data associated with user
    - **Requirement 3.6**: Require valid authentication to update profile information
    - **Requirement 3.7**: Reject attempts to update another user's profile (enforced by get_current_user)
    - **Requirement 3.8**: Return descriptive error messages when validation fails
    - **Requirement 4.4**: Validate city value is non-empty string if provided
    - **Requirement 8.2**: Validate preferences data structure
    - **Requirement 8.5**: Allow preferences to be updated independently from other profile fields
    
    **Security Notes:**
    - Users can only update their own profile (enforced by authentication)
    - Email uniqueness is enforced across all users
    - All validation is performed before any database updates
    - Partial updates are supported - unchanged fields remain as-is
    """
    # Initialize repository and service
    user_repo = UserRepository(session)
    user_service = UserService(user_repo)
    
    # Update user profile with validation
    updated_profile = user_service.update_user_profile(current_user.id, updates)
    
    return updated_profile
