"""Pet repository for database operations."""
from sqlmodel import Session, select
from typing import Optional, List
from datetime import datetime
import uuid

from app.features.pets.models import Pet
from app.common.utils import get_pht_now


class PetRepository:
    """Repository for Pet database operations.
    
    This class handles all database queries related to pets,
    following the repository pattern to abstract data access.
    """
    
    def __init__(self, session: Session):
        """Initialize the repository with a database session.
        
        Args:
            session: SQLModel database session
        """
        self.session = session
    
    def get_by_id(self, pet_id: uuid.UUID) -> Optional[Pet]:
        """Get pet by ID.
        
        Args:
            pet_id: UUID of the pet to retrieve
            
        Returns:
            Pet object if found, None otherwise
        """
        return self.session.get(Pet, pet_id)
    
    def get_all_by_owner(self, owner_id: uuid.UUID) -> List[Pet]:
        """Get all pets owned by a specific user.
        
        Args:
            owner_id: UUID of the owner
            
        Returns:
            List of Pet objects owned by the user
        """
        statement = select(Pet).where(Pet.owner_id == owner_id)
        return list(self.session.exec(statement).all())
    
    def get_all(self) -> List[Pet]:
        """Get all pets in the system (admin only).
        
        Returns:
            List of all Pet objects
        """
        statement = select(Pet)
        return list(self.session.exec(statement).all())
    
    def create(self, pet: Pet) -> Pet:
        """Create a new pet in the database.
        
        Args:
            pet: Pet object to create
            
        Returns:
            Created Pet object with database-generated fields populated
        """
        self.session.add(pet)
        self.session.flush()
        self.session.refresh(pet)
        return pet
    
    def update(self, pet: Pet) -> Pet:
        """Update an existing pet in the database.
        
        Args:
            pet: Pet object with updated fields
            
        Returns:
            Updated Pet object
        """
        pet.updated_at = get_pht_now()
        self.session.add(pet)
        self.session.flush()
        self.session.refresh(pet)
        return pet
    
    def delete(self, pet: Pet) -> None:
        """Delete a pet from the database.
        
        Args:
            pet: Pet object to delete
        """
        self.session.delete(pet)
        self.session.flush()
