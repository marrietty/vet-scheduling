"""
User service for profile management operations.

This service handles:
- User profile retrieval with sensitive data exclusion
- User profile updates with comprehensive validation
- Email uniqueness checking
- Phone and city format validation
"""

import logging
from typing import Optional
import uuid
from app.features.users.repository import UserRepository
from app.features.users.schemas import UserProfileResponse, UserProfileUpdate
from app.common.exceptions import NotFoundException, BadRequestException

# Configure logging
logger = logging.getLogger(__name__)


class UserService:
    """
    Service layer for user profile operations.
    
    This service implements business logic for viewing and updating user profiles,
    including validation for email uniqueness, phone format, and other profile fields.
    """
    
    def __init__(self, user_repo: UserRepository):
        """
        Initialize the user service.
        
        Args:
            user_repo: UserRepository instance for database operations
        """
        self.user_repo = user_repo
    
    def get_current_user_profile(self, user_id: uuid.UUID) -> UserProfileResponse:
        """
        Get the current user's profile information.
        
        This method retrieves the user's profile and transforms it into a response
        schema that excludes sensitive fields like hashed_password.
        
        Args:
            user_id: UUID of the user to retrieve
            
        Returns:
            UserProfileResponse with all non-sensitive profile information
            
        Raises:
            NotFoundException: If user is not found
            
        Requirements:
            - 2.1: Return user's full name, email, phone, city, role, and account status
            - 2.2: Do not return hashed password or other sensitive security information
        """
        logger.info(f"Retrieving profile for user: {user_id}")
        
        # Fetch user from repository
        user = self.user_repo.get_user_profile(user_id)
        if not user:
            logger.warning(f"Profile retrieval failed: User not found - {user_id}")
            raise NotFoundException("User")
        
        # Transform to response schema (excludes sensitive fields automatically)
        profile = UserProfileResponse.model_validate(user)
        
        logger.info(f"Profile retrieved successfully for user: {user_id}")
        return profile
    
    def update_user_profile(
        self, 
        user_id: uuid.UUID, 
        updates: UserProfileUpdate
    ) -> UserProfileResponse:
        """
        Update the current user's profile information.
        
        This method validates all provided updates and applies them to the user's profile.
        Validation includes:
        - Email uniqueness check (if email is being updated)
        - Empty name validation (handled by schema validator)
        - Invalid email format (handled by schema validator)
        - Invalid phone format (handled by schema validator)
        - Empty city validation (handled by schema validator)
        
        Args:
            user_id: UUID of the user to update
            updates: UserProfileUpdate schema with fields to update
            
        Returns:
            UserProfileResponse with updated profile information
            
        Raises:
            NotFoundException: If user is not found
            BadRequestException: If email is already used by another user
            
        Requirements:
            - 3.1: Validate name is not empty and update user record
            - 3.2: Validate email format and ensure not already used by another user
            - 3.3: Validate phone format and update user record
            - 3.4: Update city field in user record
            - 3.5: Store preferences data associated with user
            - 3.7: Reject attempts to update another user's profile (enforced at router level)
        """
        logger.info(f"Updating profile for user: {user_id}")
        
        # Check if user exists
        user = self.user_repo.get_user_profile(user_id)
        if not user:
            logger.warning(f"Profile update failed: User not found - {user_id}")
            raise NotFoundException("User")
        
        # Convert updates to dict, excluding None values
        update_dict = updates.model_dump(exclude_none=True)
        
        # If no updates provided, return current profile
        if not update_dict:
            logger.info(f"No updates provided for user: {user_id}")
            return UserProfileResponse.model_validate(user)
        
        # Validate email uniqueness if email is being updated (Requirement 3.2)
        if "email" in update_dict:
            new_email = update_dict["email"]
            if self.user_repo.email_exists_for_other_user(new_email, user_id):
                logger.warning(
                    f"Profile update failed: Email already in use - {new_email} (user: {user_id})"
                )
                raise BadRequestException("Email already in use")
            logger.debug(f"Email uniqueness validated for user {user_id}: {new_email}")
        
        # Note: Validation for empty name, invalid email format, invalid phone format,
        # and empty city are handled by the UserProfileUpdate schema validators
        # (Requirements 3.1, 3.2, 3.3, 4.4)
        
        # Update user via repository (Requirements 3.1, 3.3, 3.4, 3.5)
        updated_user = self.user_repo.update_user_profile(user_id, update_dict)
        
        if not updated_user:
            logger.error(f"Profile update failed: User disappeared during update - {user_id}")
            raise NotFoundException("User")
        
        # Return updated profile
        updated_profile = UserProfileResponse.model_validate(updated_user)
        
        logger.info(f"Profile updated successfully for user: {user_id}")
        logger.debug(f"Updated fields: {list(update_dict.keys())}")
        
        return updated_profile
