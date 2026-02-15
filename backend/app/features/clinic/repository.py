"""Clinic status repository for database operations."""
from sqlmodel import Session
from datetime import datetime

from app.features.clinic.models import ClinicStatus
from app.common.utils import get_pht_now


class ClinicStatusRepository:
    """Repository for ClinicStatus database operations.
    
    This class handles all database queries related to clinic status,
    following the repository pattern to abstract data access.
    
    The clinic status is stored in a single-row table with id=1.
    If the status doesn't exist, it's initialized with default "open" status.
    
    Requirements: 8.1, 8.2
    """
    
    def __init__(self, session: Session):
        """Initialize the repository with a database session.
        
        Args:
            session: SQLModel database session
        """
        self.session = session
    
    def get_current_status(self) -> ClinicStatus:
        """Get current clinic status (single row).
        
        If the status record doesn't exist, it's automatically created
        with the default "open" status.
        
        Returns:
            ClinicStatus object with current status
            
        Requirements: 8.1
        """
        status = self.session.get(ClinicStatus, 1)
        if not status:
            # Initialize with default status
            status = ClinicStatus(id=1, status="open")
            self.session.add(status)
            self.session.flush()
            self.session.refresh(status)
        return status
    
    def update_status(self, new_status: str) -> ClinicStatus:
        """Update clinic status.
        
        Updates the operational status of the clinic and sets the updated_at timestamp.
        
        Args:
            new_status: New status value (open, close, closing_soon)
            
        Returns:
            Updated ClinicStatus object
            
        Requirements: 8.2
        """
        status = self.get_current_status()
        status.status = new_status
        status.updated_at = get_pht_now()
        self.session.add(status)
        self.session.flush()
        self.session.refresh(status)
        return status
