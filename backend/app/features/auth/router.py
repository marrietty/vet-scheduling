"""
Authentication router for user registration and login endpoints.

This module provides HTTP endpoints for:
- POST /api/v1/auth/register: Register new user and return JWT token (auto-login)
- POST /api/v1/auth/login: Login existing user and return JWT token
"""

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.database import get_session
from app.features.auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.features.auth.service import AuthService
from app.features.users.repository import UserRepository
from app.infrastructure.auth import create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """
    Register a new user and return JWT token (auto-login).
    
    This endpoint:
    1. Validates email format (via Pydantic EmailStr)
    2. Checks for duplicate email
    3. Assigns role based on ADMIN_EMAIL configuration
    4. Hashes password using bcrypt
    5. Creates user in database
    6. Automatically generates and returns JWT token
    
    Args:
        request: RegisterRequest containing email and password
        session: Database session (injected dependency)
        
    Returns:
        TokenResponse with JWT access token and token type
        
    Raises:
        400 Bad Request: If email is already registered
        422 Unprocessable Entity: If email format is invalid
        
    Requirements:
        - 1.1: Create user account with hashed password
        - 1.2: Assign "admin" role if email matches ADMIN_EMAIL
        - 1.3: Assign "pet_owner" role otherwise
        - 1.4: Reject duplicate email registration
        - 1.5: Return JWT token (auto-login after registration)
        - 1.7: Hash passwords using bcrypt
        - 1.8: Validate email format
    """
    # Initialize repository and service
    user_repo = UserRepository(session)
    auth_service = AuthService(user_repo)
    
    # Register user (handles validation, role assignment, password hashing)
    user = auth_service.register(
        email=request.email,
        password=request.password,
        full_name=request.full_name
    )
    
    # Auto-login: Create JWT token for the newly registered user
    token = create_access_token({"sub": str(user.id), "role": user.role})
    
    # Commit transaction (handled by get_session dependency)
    
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """
    Login existing user and return JWT token.
    
    This endpoint:
    1. Validates credentials (email and password)
    2. Checks if user account is active
    3. Generates and returns JWT token
    
    Args:
        request: LoginRequest containing email and password
        session: Database session (injected dependency)
        
    Returns:
        TokenResponse with JWT access token and token type
        
    Raises:
        401 Unauthorized: If credentials are invalid
        403 Forbidden: If user account is deactivated
        
    Requirements:
        - 1.5: Return JWT token for valid credentials
        - 1.6: Reject login with invalid credentials
    """
    # Initialize repository and service
    user_repo = UserRepository(session)
    auth_service = AuthService(user_repo)
    
    # Authenticate user and get JWT token
    token = auth_service.login(
        email=request.email,
        password=request.password
    )
    
    return TokenResponse(access_token=token)
