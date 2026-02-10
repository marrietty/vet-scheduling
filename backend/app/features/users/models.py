"""User model for the vet clinic system."""
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from backend.app.features.pets.models import Pet


class User(SQLModel, table=True):
    """User model representing both admins and pet owners.
    
    Attributes:
        id: Unique identifier for the user
        email: User's email address (unique)
        hashed_password: Bcrypt hashed password
        role: User role - either "admin" or "pet_owner"
        phone: User's phone number (optional)
        city: User's city location (optional)
        preferences: User preferences stored as JSON (optional)
        is_active: Whether the user account is active
        created_at: Timestamp when the user was created
        pets: Relationship to pets owned by this user
    """
    __tablename__ = "users"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    full_name: str = Field(max_length=255, nullable=False)
    email: str = Field(max_length=255, unique=True, index=True, nullable=False)
    hashed_password: str = Field(max_length=255, nullable=False)
    role: str = Field(max_length=20, nullable=False)  # "admin" or "pet_owner"
    phone: Optional[str] = Field(default=None, max_length=20, nullable=True)
    city: Optional[str] = Field(default=None, max_length=100, nullable=True)
    preferences: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    pets: List["Pet"] = Relationship(back_populates="owner", cascade_delete=True)
