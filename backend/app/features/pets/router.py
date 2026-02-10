"""
Pet router for API endpoints.

This module implements the HTTP endpoints for pet management:
- POST /api/v1/pets: Create a new pet
- GET /api/v1/pets: List all pets (filtered by role)
- GET /api/v1/pets/{pet_id}: Get a specific pet
- PATCH /api/v1/pets/{pet_id}: Update a pet
- DELETE /api/v1/pets/{pet_id}: Delete a pet

All endpoints require authentication. Pet owners can only access their own pets,
while admins can access all pets.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.4
"""

from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import List
import uuid

from app.core.database import get_session
from app.common.dependencies import get_current_user
from app.features.users.models import User
from app.features.pets.models import Pet
from app.features.pets.schemas import PetCreateRequest, PetUpdateRequest, PetResponse
from app.features.pets.repository import PetRepository
from app.features.pets.service import PetService


router = APIRouter(prefix="/api/v1/pets", tags=["Pets"])


@router.post("", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
def create_pet(
    request: PetCreateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> PetResponse:
    """
    Create a new pet.
    
    The pet is automatically associated with the authenticated user as the owner.
    Returns the created pet with a computed vaccination_status field.
    
    Args:
        request: Pet creation request data
        current_user: Authenticated user (from JWT token)
        session: Database session
        
    Returns:
        Created pet with computed vaccination_status
        
    Raises:
        401: If authentication fails
        422: If request data is invalid
        
    Requirements: 3.1, 4.4
    """
    pet_repo = PetRepository(session)
    pet_service = PetService(pet_repo)
    
    pet = pet_service.create_pet(
        name=request.name,
        species=request.species,
        breed=request.breed,
        date_of_birth=request.date_of_birth,
        last_vaccination=request.last_vaccination,
        medical_history=request.medical_history,
        notes=request.notes,
        current_user=current_user
    )
    
    session.commit()
    
    # Return response with computed vaccination status
    return PetResponse.from_pet(pet)


@router.get("", response_model=List[PetResponse])
def get_pets(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> List[PetResponse]:
    """
    Get all pets (filtered by role).
    
    - Admin users: Returns all pets in the system
    - Pet owners: Returns only pets owned by the authenticated user
    
    All pets include a computed vaccination_status field.
    
    Args:
        current_user: Authenticated user (from JWT token)
        session: Database session
        
    Returns:
        List of pets with computed vaccination_status
        
    Raises:
        401: If authentication fails
        
    Requirements: 3.2, 3.3, 4.4
    """
    pet_repo = PetRepository(session)
    pet_service = PetService(pet_repo)
    
    pets = pet_service.get_pets(current_user)
    
    # Return responses with computed vaccination status
    return [PetResponse.from_pet(pet) for pet in pets]


@router.get("/{pet_id}", response_model=PetResponse)
def get_pet(
    pet_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> PetResponse:
    """
    Get a specific pet.
    
    - Admin users: Can access any pet
    - Pet owners: Can only access their own pets
    
    Returns the pet with a computed vaccination_status field.
    
    Args:
        pet_id: UUID of the pet to retrieve
        current_user: Authenticated user (from JWT token)
        session: Database session
        
    Returns:
        Pet with computed vaccination_status
        
    Raises:
        401: If authentication fails
        403: If pet owner tries to access another user's pet
        404: If pet doesn't exist
        
    Requirements: 3.4, 4.4
    """
    pet_repo = PetRepository(session)
    pet_service = PetService(pet_repo)
    
    pet = pet_service.get_pet_by_id(pet_id, current_user)
    
    # Return response with computed vaccination status
    return PetResponse.from_pet(pet)


@router.patch("/{pet_id}", response_model=PetResponse)
def update_pet(
    pet_id: uuid.UUID,
    request: PetUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> PetResponse:
    """
    Update a pet.
    
    - Admin users: Can update any pet
    - Pet owners: Can only update their own pets
    
    Only provided fields are updated (partial update support).
    Returns the updated pet with a computed vaccination_status field.
    
    Args:
        pet_id: UUID of the pet to update
        request: Pet update request data (all fields optional)
        current_user: Authenticated user (from JWT token)
        session: Database session
        
    Returns:
        Updated pet with computed vaccination_status
        
    Raises:
        401: If authentication fails
        403: If pet owner tries to update another user's pet
        404: If pet doesn't exist
        422: If request data is invalid
        
    Requirements: 3.5, 4.4
    """
    pet_repo = PetRepository(session)
    pet_service = PetService(pet_repo)
    
    pet = pet_service.update_pet(
        pet_id=pet_id,
        current_user=current_user,
        **request.model_dump(exclude_unset=True)
    )
    
    session.commit()
    
    # Return response with computed vaccination status
    return PetResponse.from_pet(pet)


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(
    pet_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> None:
    """
    Delete a pet.
    
    - Admin users: Can delete any pet
    - Pet owners: Can only delete their own pets
    
    Args:
        pet_id: UUID of the pet to delete
        current_user: Authenticated user (from JWT token)
        session: Database session
        
    Returns:
        No content (204 status code)
        
    Raises:
        401: If authentication fails
        403: If pet owner tries to delete another user's pet
        404: If pet doesn't exist
        
    Requirements: 3.6
    """
    pet_repo = PetRepository(session)
    pet_service = PetService(pet_repo)
    
    pet_service.delete_pet(pet_id, current_user)
    
    session.commit()
