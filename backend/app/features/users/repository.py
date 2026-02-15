"""User repository for database operations."""
from sqlmodel import Session, select
from typing import Optional
import uuid

from app.features.users.models import User


class UserRepository:
    """Repository for User database operations.
    
    This class handles all database queries related to users,
    following the repository pattern to abstract data access.
    """
    
    def __init__(self, session: Session):
        """Initialize the repository with a database session.
        
        Args:
            session: SQLModel database session
        """
        self.session = session
    
    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID.
        
        Args:
            user_id: UUID of the user to retrieve
            
        Returns:
            User object if found, None otherwise
        """
        return self.session.get(User, user_id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User object if found, None otherwise
        """
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()
    
    def create(self, user: User) -> User:
        """Create a new user in the database.
        
        Args:
            user: User object to create
            
        Returns:
            Created User object with database-generated fields populated
        """
        self.session.add(user)
        self.session.flush()
        self.session.refresh(user)
        return user
    
    def get_user_profile(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user profile by ID.
        
        Args:
            user_id: UUID of the user to retrieve
            
        Returns:
            User object if found, None otherwise
        """
        return self.session.get(User, user_id)
    
    def update_user_profile(self, user_id: uuid.UUID, updates: dict) -> Optional[User]:
        """Update user profile with provided fields.
        
        Args:
            user_id: UUID of the user to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated User object if found, None otherwise
        """
        user = self.session.get(User, user_id)
        if user is None:
            return None
        
        # Update only the fields provided in the updates dictionary
        for key, value in updates.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self.session.add(user)
        self.session.flush()
        self.session.refresh(user)
        return user
    
    def email_exists_for_other_user(self, email: str, user_id: uuid.UUID) -> bool:
        """Check if an email is already used by a different user.
        
        Args:
            email: Email address to check
            user_id: UUID of the current user (to exclude from check)
            
        Returns:
            True if email exists for another user, False otherwise
        """
        statement = select(User).where(User.email == email, User.id != user_id)
        existing_user = self.session.exec(statement).first()
        return existing_user is not None

    def delete_user(self, user_id: uuid.UUID) -> bool:
        """Delete a user permanently from the database.
        
        Cascade deletion of pets and appointments is handled by
        the SQLModel relationship configuration (cascade_delete=True).
        
        Args:
            user_id: UUID of the user to delete
            
        Returns:
            True if user was deleted, False if not found
        """
        user = self.session.get(User, user_id)
        if user is None:
            return False
        
        self.session.delete(user)
        self.session.flush()
        return True
