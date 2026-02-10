"""
Migration script to add 'notes' column to pets table.

This script adds the notes field to support enhanced pet profile information
as specified in Requirement 5 of the vet-clinic-enhancements spec.
"""

import sys
from sqlalchemy import text
from app.core.database import engine

def migrate_add_notes():
    """Add notes column to pets table."""
    
    print("=" * 60)
    print("MIGRATION: Add notes column to pets table")
    print("=" * 60)
    print("\nThis script will:")
    print("  1. Check if 'notes' column exists in pets table")
    print("  2. Add the column if it doesn't exist")
    print("  3. Set default value to NULL for existing records")
    
    response = input("\nDo you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\n❌ Migration cancelled.")
        return
    
    print("\n" + "=" * 60)
    print("Starting migration...")
    print("=" * 60)
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            print("\n1. Checking if 'notes' column exists...")
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='pets' AND column_name='notes'
            """))
            
            if result.fetchone():
                print("   ℹ️  Column 'notes' already exists. No migration needed.")
                return
            
            print("   ✓ Column 'notes' does not exist. Proceeding with migration...")
            
            # Add notes column
            print("\n2. Adding 'notes' column to pets table...")
            conn.execute(text("""
                ALTER TABLE pets 
                ADD COLUMN notes TEXT NULL
            """))
            conn.commit()
            print("   ✓ Column 'notes' added successfully")
            
            print("\n" + "=" * 60)
            print("✅ Migration completed successfully!")
            print("=" * 60)
            
            print("\nThe pets table now includes:")
            print("  ✓ notes column (TEXT, nullable)")
            print("\nExisting pet records will have notes=NULL by default.")
            print("\nYou can now:")
            print("  1. Restart the API server if it's running")
            print("  2. Create pets with notes field")
            print("  3. Update existing pets to add notes")
            
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        print("\nPlease check:")
        print("  1. DATABASE_URL is correct in .env file")
        print("  2. Database server is running")
        print("  3. You have permission to ALTER tables")
        print("  4. The pets table exists")
        sys.exit(1)

if __name__ == "__main__":
    migrate_add_notes()
