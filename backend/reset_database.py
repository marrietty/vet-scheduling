"""
Database reset script - drops all tables and recreates them.

WARNING: This will delete ALL data in the database!
Only use this in development.
"""

import sys
from sqlmodel import SQLModel
from app.core.database import engine
from app.features.users.models import User
from app.features.pets.models import Pet
from app.features.appointments.models import Appointment
from app.features.clinic.models import ClinicStatus
from app.features.auth.models import TokenBlacklist

def reset_database():
    """Drop all tables and recreate them."""
    
    print("=" * 60)
    print("DATABASE RESET SCRIPT")
    print("=" * 60)
    print("\n⚠️  WARNING: This will DELETE ALL DATA in the database!")
    print("\nThis script will:")
    print("  1. Drop all existing tables")
    print("  2. Recreate tables with current schema")
    print("  3. Initialize clinic status to 'open'")
    
    response = input("\nAre you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\n❌ Database reset cancelled.")
        return
    
    print("\n" + "=" * 60)
    print("Starting database reset...")
    print("=" * 60)
    
    try:
        # Drop all tables
        print("\n1. Dropping all tables...")
        SQLModel.metadata.drop_all(engine)
        print("   ✓ All tables dropped")
        
        # Create all tables
        print("\n2. Creating tables with current schema...")
        SQLModel.metadata.create_all(engine)
        print("   ✓ All tables created")
        
        # Initialize clinic status
        print("\n3. Initializing clinic status...")
        from sqlmodel import Session
        with Session(engine) as session:
            clinic_status = ClinicStatus(id=1, status="open")
            session.add(clinic_status)
            session.commit()
        print("   ✓ Clinic status initialized to 'open'")
        
        print("\n" + "=" * 60)
        print("✅ Database reset completed successfully!")
        print("=" * 60)
        
        print("\nDatabase schema is now up to date with:")
        print("  ✓ users table")
        print("  ✓ pets table")
        print("  ✓ appointments table (with user_id column)")
        print("  ✓ clinic_status table")
        print("  ✓ token_blacklist table")
        
        print("\nYou can now:")
        print("  1. Start the API server: uvicorn app.main:app --reload")
        print("  2. Register users at: POST /api/v1/auth/register")
        print("  3. Create pets and appointments")
        
    except Exception as e:
        print(f"\n❌ Error during database reset: {e}")
        print("\nPlease check:")
        print("  1. DATABASE_URL is correct in .env file")
        print("  2. Database server is running")
        print("  3. You have permission to drop/create tables")
        sys.exit(1)

if __name__ == "__main__":
    reset_database()
