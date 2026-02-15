"""Appointment model for the vet clinic system."""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import uuid

from app.common.utils import get_pht_now

if TYPE_CHECKING:
    from app.features.pets.models import Pet
    from app.features.users.models import User


class Appointment(SQLModel, table=True):
    """Appointment model representing scheduled visits for pets.
    
    Attributes:
        id: Unique identifier for the appointment
        start_time: When the appointment starts
        end_time: When the appointment ends (calculated based on service type)
        service_type: Type of service (vaccination, routine, surgery, emergency)
        status: Current status (pending, confirmed, cancelled, completed)
        notes: Optional notes about the appointment
        pet_id: Foreign key to the pet this appointment is for
        user_id: Foreign key to the user who booked the appointment
        created_at: Timestamp when the appointment was created
        updated_at: Timestamp when the appointment was last updated
        pet: Relationship to the Pet this appointment is for
        user: Relationship to the User who booked this appointment
    """
    __tablename__ = "appointments"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    start_time: datetime = Field(index=True, nullable=False)
    end_time: datetime = Field(index=True, nullable=False)
    service_type: str = Field(max_length=20, nullable=False)  # vaccination, routine, surgery, emergency
    status: str = Field(max_length=20, default="pending")  # pending, confirmed, cancelled, completed
    notes: Optional[str] = Field(default=None)
    
    # Foreign keys
    pet_id: uuid.UUID = Field(foreign_key="pets.id", index=True, ondelete="CASCADE")
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    
    # Timestamps
    created_at: datetime = Field(default_factory=get_pht_now)
    updated_at: datetime = Field(default_factory=get_pht_now)
    
    # Relationships
    pet: "Pet" = Relationship(back_populates="appointments")
    user: "User" = Relationship()
