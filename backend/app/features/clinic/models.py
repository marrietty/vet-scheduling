"""ClinicStatus model for the vet clinic system."""
from sqlmodel import SQLModel, Field
from datetime import datetime

from app.common.utils import get_pht_now


class ClinicStatus(SQLModel, table=True):
    """ClinicStatus model representing the operational status of the clinic.
    
    This is a single-row table that stores the current operational status of the clinic.
    The id is always 1 to ensure only one status record exists.
    
    Attributes:
        id: Primary key, always set to 1 (single-row table)
        status: Current operational status (open, close, closing_soon)
        updated_at: Timestamp when the status was last updated
    """
    __tablename__ = "clinic_status"
    
    id: int = Field(default=1, primary_key=True)
    status: str = Field(max_length=20, default="open")
    updated_at: datetime = Field(default_factory=get_pht_now)
