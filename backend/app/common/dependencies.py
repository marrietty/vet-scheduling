"""
FastAPI dependencies for authentication and authorization.

This module provides dependency functions for:
- JWT token extraction and validation
- User authentication (get_current_user)
- Role-based access control (require_role)
"""

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from typing import List
import uuid

from app.core.database import get_session
from app.infrastructure.auth import verify_token
from app.features.users.models import User
from app.features.users.repository import UserRepository
from app.features.auth.repository import TokenBlacklistRepository
from app.features.auth.service import AuthService
from app.common.exceptions import UnauthorizedException, NotFoundException, ForbiddenException

# HTTP Bearer token security scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Get authenticated user from JWT token.
    
    This dependency extracts the JWT token from the Authorization header,
    validates it, checks if it's blacklisted, retrieves the user from the 
    database, and checks if the user account is active.
    
    Args:
        credentials: HTTP Bearer token credentials from the request header
        session: Database session dependency
        
    Returns:
        Authenticated User object
        
    Raises:
        UnauthorizedException: If token is invalid, expired, blacklisted, or missing user ID
        NotFoundException: If user ID from token doesn't exist in database
        ForbiddenException: If user account is deactivated
        
    Example:
        @router.get("/protected")
        def protected_endpoint(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id, "role": current_user.role}
    
    Requirements:
        - 2.5: Extract user identity and role from valid JWT token
        - 2.6: Reject invalid or expired JWT tokens
        - 2.7: Reject requests with no JWT token
        - 1.2: Reject blacklisted tokens
    """
    # Extract token from credentials
    token = credentials.credentials
    
    # Verify and decode token (raises UnauthorizedException if invalid)
    payload = verify_token(token)
    
    # Check if token is blacklisted (Requirement 1.2)
    token_blacklist_repo = TokenBlacklistRepository(session)
    user_repo = UserRepository(session)
    auth_service = AuthService(user_repo, token_blacklist_repo)
    auth_service.verify_token_not_blacklisted(token)
    
    # Extract user ID from token payload
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Invalid token: missing user ID")
    
    # Convert string UUID to UUID object
    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, AttributeError):
        raise UnauthorizedException("Invalid token: malformed user ID")
    
    # Retrieve user from database
    user = user_repo.get_by_id(user_id)
    
    if not user:
        raise NotFoundException("User")
    
    # Check if user account is active
    if not user.is_active:
        raise ForbiddenException("Account is deactivated")
    
    return user


def require_role(allowed_roles: List[str]):
    """
    Dependency factory for role-based access control.
    
    This function returns a dependency that checks if the authenticated user
    has one of the allowed roles. It should be used for endpoints that require
    specific roles (e.g., admin-only endpoints).
    
    Args:
        allowed_roles: List of role strings that are allowed to access the endpoint
                      (e.g., ["admin"] or ["admin", "pet_owner"])
        
    Returns:
        A dependency function that validates user role
        
    Raises:
        ForbiddenException: If user's role is not in the allowed roles list
        
    Example:
        # Admin-only endpoint
        @router.patch("/clinic/status")
        def update_clinic_status(
            current_user: User = Depends(require_role(["admin"])),
            ...
        ):
            return {"status": "updated"}
        
        # Endpoint accessible by both roles
        @router.get("/appointments")
        def get_appointments(
            current_user: User = Depends(require_role(["admin", "pet_owner"])),
            ...
        ):
            return []
    
    Requirements:
        - 2.1: Grant full access to admins
        - 2.4: Reject pet owners from admin-only endpoints
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        """
        Check if current user has required role.
        
        Args:
            current_user: Authenticated user from get_current_user dependency
            
        Returns:
            The current user if role check passes
            
        Raises:
            ForbiddenException: If user's role is not in allowed roles
        """
        if current_user.role not in allowed_roles:
            raise ForbiddenException(
                f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker
