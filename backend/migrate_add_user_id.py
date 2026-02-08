"""
Migration script to add user_id column to appointments table.

This is a safer alternative to reset_database.py as it preserves existing data.
"""

import sys
from sqlalchemy import text
from app.core.database import engine

def migrate_add_user_id():
    """Add user_id column to appointments table if it doesn't exist."""
    
    print("=" * 60)
    print("MIGRATION: Add user_id to appointments table")
    print("=" * 60)
    
    try:
        with engine.connect() as conn:
            # Check if column exists
            print("\n1. Checking if user_id column exists...")
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='appointments' AND column_name='user_id'
            """))
            
            if result.fetchone():
                print("   ℹ️  user_id column already exists. No migration needed.")
                return
            
            print("   ⚠️  user_id column does not exist. Adding it...")
            
            # Add the column
            print("\n2. Adding user_id column...")
            conn.execute(text("""
                ALTER TABLE appointments 
                ADD COLUMN user_id UUID
            """))
            conn.commit()
            print("   ✓ Column added")
            
            # Add foreign key constraint
            print("\n3. Adding foreign key constraint...")
            conn.execute(text("""
                ALTER TABLE appointments 
                ADD CONSTRAINT appointments_user_id_fkey 
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            """))
            conn.commit()
            print("   ✓ Foreign key constraint added")
            
            # Add index
            print("\n4. Adding index on user_id...")
            conn.execute(text("""
                CREATE INDEX ix_appointments_user_id ON appointments(user_id)
            """))
            conn.commit()
            print("   ✓ Index added")
            
            # Update existing appointments with user_id from pet owner
            print("\n5. Updating existing appointments with user_id from pet owners...")
            result = conn.execute(text("""
                UPDATE appointments 
                SET user_id = pets.owner_id 
                FROM pets 
                WHERE appointments.pet_id = pets.id
            """))
            conn.commit()
            rows_updated = result.rowcount
            print(f"   ✓ Updated {rows_updated} existing appointments")
            
            # Make column NOT NULL
            print("\n6. Making user_id column NOT NULL...")
            conn.execute(text("""
                ALTER TABLE appointments 
                ALTER COLUMN user_id SET NOT NULL
            """))
            conn.commit()
            print("   ✓ Column set to NOT NULL")
            
            print("\n" + "=" * 60)
            print("✅ Migration completed successfully!")
            print("=" * 60)
            
            print("\nChanges made:")
            print("  ✓ Added user_id column to appointments table")
            print("  ✓ Added foreign key constraint to users table")
            print("  ✓ Added index on user_id for performance")
            print(f"  ✓ Updated {rows_updated} existing appointments")
            print("  ✓ Set user_id as NOT NULL")
            
            print("\nYou can now restart the API server.")
            
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\nPossible issues:")
        print("  1. Database connection failed")
        print("  2. Insufficient permissions")
        print("  3. Existing appointments have no matching pets")
        print("\nIf migration fails, you can use reset_database.py instead")
        print("(WARNING: reset_database.py will delete all data)")
        sys.exit(1)

if __name__ == "__main__":
    migrate_add_user_id()
