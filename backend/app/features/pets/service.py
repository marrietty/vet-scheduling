"""
Pet service layer for business logic.

This module implements the business logic for pet management including:
- Pet creation with ownership association
- Pet retrieval with role-based filtering
- Pet updates with ownership validation
- Pet deletion with ownership validation

Requirements: 2.2, 3.1, 3.2, 3.3, 3.5, 3.6, 3.7
"""

from typing import List, Optional
from datetime import date, datetime
import uuid

from app.features.pets.models import Pet
from app.features.pets.repository import PetRepository
from app.features.users.models import User
from app.common.exceptions import NotFoundException, ForbiddenException


class PetService:
    """
    Service layer for pet management operations.
    
    This class implements business logic and authorization rules for pet operations,
    coordinating between the router layer and repository layer.
    """
    
    def __init__(self, pet_repo: PetRepository):
        """
        Initialize the service with a pet repository.
        
        Args:
            pet_repo: PetRepository instance for database operations
        """
        self.pet_repo = pet_repo
    
    def create_pet(
        self,
        name: str,
        species: str,
        current_user: User,
        breed: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        last_vaccination: Optional[datetime] = None,
        medical_history: dict = None,
        notes: Optional[str] = None
    ) -> Pet:
        """
        Create a new pet owned by the current user.
        
        The pet is automatically associated with the authenticated user as the owner.
        
        Args:
            name: Pet's name
            species: Type of animal (e.g., dog, cat, bird)
            current_user: Authenticated user who will own the pet
            breed: Specific breed (optional)
            date_of_birth: Pet's date of birth (optional)
            last_vaccination: Date of last vaccination (optional)
            medical_history: JSON object storing medical records (optional)
            notes: Additional notes about the pet (optional)
        
        Returns:
            Created Pet object
        
        Requirements: 3.1, 5.2
        """
        if medical_history is None:
            medical_history = {}
        
        pet = Pet(
            name=name,
            species=species,
            breed=breed,
            date_of_birth=date_of_birth,
            last_vaccination=last_vaccination,
            medical_history=medical_history,
            notes=notes,
            owner_id=current_user.id
        )
        
        return self.pet_repo.create(pet)
    
    def get_pets(self, current_user: User) -> List[Pet]:
        """
        Get pets based on user role.
        
        - Admin users: Returns all pets in the system
        - Pet owners: Returns only pets owned by the user
        
        Args:
            current_user: Authenticated user
        
        Returns:
            List of Pet objects accessible to the user
        
        Requirements: 2.2, 3.2, 3.3
        """
        if current_user.role == "admin":
            return self.pet_repo.get_all()
        else:
            return self.pet_repo.get_all_by_owner(current_user.id)
    
    def get_pet_by_id(self, pet_id: uuid.UUID, current_user: User) -> Pet:
        """
        Get a specific pet with ownership validation.
        
        - Admin users: Can access any pet
        - Pet owners: Can only access their own pets
        
        Args:
            pet_id: UUID of the pet to retrieve
            current_user: Authenticated user
        
        Returns:
            Pet object if found and authorized
        
        Raises:
            NotFoundException: If pet doesn't exist
            ForbiddenException: If pet owner tries to access another user's pet
        
        Requirements: 2.2, 3.4
        """
        pet = self.pet_repo.get_by_id(pet_id)
        if not pet:
            raise NotFoundException("Pet")
        
        # Validate ownership for pet owners
        if current_user.role == "pet_owner" and pet.owner_id != current_user.id:
            raise ForbiddenException("You can only access your own pets")
        
        return pet
    
    def update_pet(
        self,
        pet_id: uuid.UUID,
        current_user: User,
        name: Optional[str] = None,
        species: Optional[str] = None,
        breed: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        last_vaccination: Optional[datetime] = None,
        medical_history: Optional[dict] = None,
        notes: Optional[str] = None
    ) -> Pet:
        """
        Update a pet with ownership validation.
        
        - Admin users: Can update any pet
        - Pet owners: Can only update their own pets
        
        Only provided fields are updated (partial update support).
        
        Args:
            pet_id: UUID of the pet to update
            current_user: Authenticated user
            name: Pet's name (optional)
            species: Type of animal (optional)
            breed: Specific breed (optional)
            date_of_birth: Pet's date of birth (optional)
            last_vaccination: Date of last vaccination (optional)
            medical_history: JSON object storing medical records (optional)
            notes: Additional notes about the pet (optional)
        
        Returns:
            Updated Pet object
        
        Raises:
            NotFoundException: If pet doesn't exist
            ForbiddenException: If pet owner tries to update another user's pet
        
        Requirements: 3.5, 3.7, 5.3
        """
        # Get pet and validate ownership
        pet = self.get_pet_by_id(pet_id, current_user)
        
        # Update fields if provided
        if name is not None:
            pet.name = name
        if species is not None:
            pet.species = species
        if breed is not None:
            pet.breed = breed
        if date_of_birth is not None:
            pet.date_of_birth = date_of_birth
        if last_vaccination is not None:
            pet.last_vaccination = last_vaccination
        if medical_history is not None:
            pet.medical_history = medical_history
        if notes is not None:
            pet.notes = notes
        
        return self.pet_repo.update(pet)
    
    def delete_pet(self, pet_id: uuid.UUID, current_user: User) -> None:
        """
        Delete a pet with ownership validation.
        
        - Admin users: Can delete any pet
        - Pet owners: Can only delete their own pets
        
        Args:
            pet_id: UUID of the pet to delete
            current_user: Authenticated user
        
        Raises:
            NotFoundException: If pet doesn't exist
            ForbiddenException: If pet owner tries to delete another user's pet
        
        Requirements: 3.6, 3.7
        """
        # Get pet and validate ownership
        pet = self.get_pet_by_id(pet_id, current_user)
        
        # Delete the pet
        self.pet_repo.delete(pet)
