"""Pet model for the vet clinic system."""
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
import uuid

from app.common.utils import get_pht_now

if TYPE_CHECKING:
    from app.features.users.models import User
    from app.features.appointments.models import Appointment


class Pet(SQLModel, table=True):
    """Pet model representing animals registered in the system.
    
    Attributes:
        id: Unique identifier for the pet
        name: Pet's name
        species: Type of animal (e.g., dog, cat, bird)
        breed: Specific breed (optional)
        date_of_birth: Pet's date of birth (optional)
        last_vaccination: Date of last vaccination (optional)
        medical_history: JSON field storing medical records and notes
        notes: Additional notes about the pet (optional)
        owner_id: Foreign key to the user who owns this pet
        created_at: Timestamp when the pet was registered
        updated_at: Timestamp when the pet was last updated
        owner: Relationship to the User who owns this pet
        appointments: Relationship to appointments for this pet
    """
    __tablename__ = "pets"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=100, nullable=False)
    species: str = Field(max_length=50, nullable=False)
    breed: Optional[str] = Field(default=None, max_length=100)
    date_of_birth: Optional[date] = Field(default=None)
    last_vaccination: Optional[datetime] = Field(default=None)
    medical_history: dict = Field(default_factory=dict, sa_column=Column(JSON))
    notes: Optional[str] = Field(default=None)
    
    # Foreign key
    owner_id: uuid.UUID = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    
    # Timestamps
    created_at: datetime = Field(default_factory=get_pht_now)
    updated_at: datetime = Field(default_factory=get_pht_now)
    
    # Relationships
    owner: "User" = Relationship(back_populates="pets")
    appointments: List["Appointment"] = Relationship(back_populates="pet", cascade_delete=True)
