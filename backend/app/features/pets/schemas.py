"""
Pet request and response schemas for the Vet Clinic Scheduling System.

This module defines Pydantic schemas for pet-related API operations:
- PetCreateRequest: Schema for creating a new pet
- PetUpdateRequest: Schema for updating an existing pet
- PetResponse: Schema for pet responses with computed vaccination status

Requirements: 3.1, 3.4, 4.4
"""

from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
import uuid

from app.common.utils import get_vaccination_status


class PetCreateRequest(BaseModel):
    """
    Request schema for creating a new pet.
    
    Attributes:
        name: Pet's name (required)
        species: Type of animal (required)
        breed: Specific breed (optional)
        date_of_birth: Pet's date of birth (optional)
        last_vaccination: Date of last vaccination (optional)
        medical_history: JSON object storing medical records (default: empty dict)
        notes: Additional notes about the pet (optional)
    
    Requirements: 3.1, 5.2
    """
    name: str = Field(..., min_length=1, max_length=100, description="Pet's name")
    species: str = Field(..., min_length=1, max_length=50, description="Type of animal (e.g., dog, cat, bird)")
    breed: Optional[str] = Field(None, max_length=100, description="Specific breed")
    date_of_birth: Optional[date] = Field(None, description="Pet's date of birth")
    last_vaccination: Optional[datetime] = Field(None, description="Date of last vaccination")
    medical_history: dict = Field(default_factory=dict, description="JSON object storing medical records and notes")
    notes: Optional[str] = Field(None, description="Additional notes about the pet")


class PetUpdateRequest(BaseModel):
    """
    Request schema for updating an existing pet.
    
    All fields are optional to support partial updates.
    
    Attributes:
        name: Pet's name (optional)
        species: Type of animal (optional)
        breed: Specific breed (optional)
        date_of_birth: Pet's date of birth (optional)
        last_vaccination: Date of last vaccination (optional)
        medical_history: JSON object storing medical records (optional)
        notes: Additional notes about the pet (optional)
    
    Requirements: 3.1, 5.3
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Pet's name")
    species: Optional[str] = Field(None, min_length=1, max_length=50, description="Type of animal")
    breed: Optional[str] = Field(None, max_length=100, description="Specific breed")
    date_of_birth: Optional[date] = Field(None, description="Pet's date of birth")
    last_vaccination: Optional[datetime] = Field(None, description="Date of last vaccination")
    medical_history: Optional[dict] = Field(None, description="JSON object storing medical records and notes")
    notes: Optional[str] = Field(None, description="Additional notes about the pet")


class PetResponse(BaseModel):
    """
    Response schema for pet data.
    
    Includes all pet fields plus a computed vaccination_status field.
    The vaccination_status is computed based on the last_vaccination date:
    - "unknown": No vaccination date recorded
    - "expired": Last vaccination was more than 365 days ago
    - "valid": Last vaccination was 365 days or less ago
    
    Attributes:
        id: Unique identifier for the pet
        name: Pet's name
        species: Type of animal
        breed: Specific breed (optional)
        date_of_birth: Pet's date of birth (optional)
        last_vaccination: Date of last vaccination (optional)
        vaccination_status: Computed vaccination status (valid, expired, unknown)
        medical_history: JSON object storing medical records
        notes: Additional notes about the pet (optional)
        owner_id: ID of the user who owns this pet
        created_at: Timestamp when the pet was registered
        updated_at: Timestamp when the pet was last updated
    
    Requirements: 3.4, 4.4, 5.4
    """
    id: uuid.UUID
    name: str
    species: str
    breed: Optional[str]
    date_of_birth: Optional[date]
    last_vaccination: Optional[datetime]
    vaccination_status: str = Field(..., description="Computed vaccination status: valid, expired, or unknown")
    medical_history: dict
    notes: Optional[str]
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
    
    @classmethod
    def from_pet(cls, pet) -> "PetResponse":
        """
        Create a PetResponse from a Pet model instance.
        
        This method automatically computes the vaccination_status field
        based on the pet's last_vaccination date.
        
        Args:
            pet: Pet model instance
        
        Returns:
            PetResponse with computed vaccination_status
        
        Requirements: 4.4, 5.4
        """
        return cls(
            id=pet.id,
            name=pet.name,
            species=pet.species,
            breed=pet.breed,
            date_of_birth=pet.date_of_birth,
            last_vaccination=pet.last_vaccination,
            vaccination_status=get_vaccination_status(pet.last_vaccination),
            medical_history=pet.medical_history,
            notes=pet.notes,
            owner_id=pet.owner_id,
            created_at=pet.created_at,
            updated_at=pet.updated_at
        )
