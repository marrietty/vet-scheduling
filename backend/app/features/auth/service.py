"""
Authentication service for user registration and login.

This service handles:
- User registration with role assignment based on ADMIN_EMAIL
- Password hashing and verification
- Duplicate email checking
- JWT token generation for authenticated users
"""

import logging
from typing import TYPE_CHECKING
from app.features.users.repository import UserRepository
from app.features.users.models import User
from app.infrastructure.auth import hash_password, verify_password, create_access_token
from app.common.exceptions import BadRequestException, UnauthorizedException, ForbiddenException
from app.core import config

if TYPE_CHECKING:
    pass

# Configure logging
logger = logging.getLogger(__name__)


class AuthService:
    """
    Service layer for authentication operations.
    
    This service implements business logic for user registration and login,
    including role assignment, password hashing, and JWT token generation.
    """
    
    def __init__(self, user_repo: UserRepository):
        """
        Initialize the authentication service.
        
        Args:
            user_repo: UserRepository instance for database operations
        """
        self.user_repo = user_repo
    
    def register(self, email: str, password: str, full_name: str) -> User:
        """
        Register a new user with role assignment based on email.
        
        This method:
        1. Checks if email already exists (raises BadRequestException if duplicate)
        2. Determines role based on ADMIN_EMAIL configuration
        3. Hashes the password using bcrypt
        4. Creates and returns the new user
        
        Args:
            email: User's email address
            password: User's plaintext password (will be hashed)
            
        Returns:
            Created User object with hashed password and assigned role
            
        Raises:
            BadRequestException: If email is already registered or password invalid
            
        Requirements:
            - 1.1: Create user account with hashed password
            - 1.2: Assign "admin" role if email matches ADMIN_EMAIL
            - 1.3: Assign "pet_owner" role if email doesn't match ADMIN_EMAIL
            - 1.4: Reject registration with existing email
            - 1.7: Hash passwords using bcrypt
        """
        logger.info(f"Registration attempt for email: {email}")
        
        # Check if email already exists (Requirement 1.4)
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            logger.warning(f"Registration failed: Email already exists - {email}")
            raise BadRequestException("Email already registered")
        
        # Determine role based on email (Requirements 1.2, 1.3)
        role = "admin" if email == config.ADMIN_EMAIL else "pet_owner"
        logger.debug(f"Assigning role '{role}' to user {email}")
        
        # Hash password (Requirement 1.7) - validation happens in hash_password
        try:
            hashed_password = hash_password(password)
        except BadRequestException as e:
            logger.warning(f"Registration failed for {email}: {str(e)}")
            raise
        
        # Create user (Requirement 1.1)
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role
        )
        
        created_user = self.user_repo.create(user)
        logger.info(f"User registered successfully: {email} (role: {role})")
        
        return created_user
    
    def login(self, email: str, password: str) -> str:
        """
        Authenticate user and return JWT token.
        
        This method:
        1. Retrieves user by email
        2. Verifies password against stored hash
        3. Checks if user account is active
        4. Generates and returns JWT token
        
        Args:
            email: User's email address
            password: User's plaintext password
            
        Returns:
            JWT access token string
            
        Raises:
            UnauthorizedException: If credentials are invalid
            ForbiddenException: If user account is deactivated
            
        Requirements:
            - 1.5: Return JWT token for valid credentials
            - 1.6: Reject login with invalid credentials
        """
        logger.info(f"Login attempt for email: {email}")
        
        # Get user by email (Requirement 1.6)
        user = self.user_repo.get_by_email(email)
        if not user:
            logger.warning(f"Login failed: User not found - {email}")
            raise UnauthorizedException("Invalid credentials")
        
        # Verify password (Requirement 1.6)
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Login failed: Invalid password for {email}")
            raise UnauthorizedException("Invalid credentials")
        
        # Check if active
        if not user.is_active:
            logger.warning(f"Login failed: Account deactivated - {email}")
            raise ForbiddenException("Account is deactivated")
        
        # Create JWT token (Requirement 1.5)
        token_data = {"sub": str(user.id), "role": user.role}
        access_token = create_access_token(token_data)
        
        logger.info(f"Login successful for {email} (role: {user.role})")
        
        return access_token
