# Database Management Guide

## Issue: Missing user_id Column

### Error Message
```
psycopg2.errors.UndefinedColumn: column appointments.user_id does not exist
```

### Cause
The database schema is out of sync with the application models. The `appointments` table is missing the `user_id` column that was added to the `Appointment` model.

## Solutions

You have two options to fix this:

### Option 1: Migration Script (Recommended - Preserves Data)

This option adds the missing column without deleting existing data.

```bash
cd backend
python migrate_add_user_id.py
```

**What it does:**
1. Checks if `user_id` column exists
2. Adds the column if missing
3. Adds foreign key constraint to `users` table
4. Adds index for performance
5. Updates existing appointments with `user_id` from pet owners
6. Sets column as NOT NULL

**Pros:**
- ✅ Preserves all existing data
- ✅ Safe for production
- ✅ Can be run multiple times (idempotent)

**Cons:**
- ❌ Requires existing appointments to have valid pets
- ❌ More complex

### Option 2: Database Reset (Development Only - Deletes All Data)

This option drops all tables and recreates them with the current schema.

```bash
cd backend
python reset_database.py
```

**What it does:**
1. Drops all existing tables
2. Recreates tables with current schema
3. Initializes clinic status to "open"

**Pros:**
- ✅ Simple and fast
- ✅ Guaranteed to match current schema
- ✅ Good for development

**Cons:**
- ❌ **DELETES ALL DATA**
- ❌ Not suitable for production
- ❌ Requires re-registering users

## Recommended Approach

### For Development:
Use **Option 2 (Database Reset)** if you don't have important data:
```bash
python reset_database.py
```

### For Production or Important Data:
Use **Option 1 (Migration Script)**:
```bash
python migrate_add_user_id.py
```

## After Running Migration

1. **Restart the API server:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Verify the fix:**
   - Try deleting a pet again
   - Check that appointments work correctly
   - No more `user_id does not exist` errors

## Database Schema

### Current Schema (After Migration)

#### users table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL
);
```

#### pets table
```sql
CREATE TABLE pets (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    species VARCHAR(50) NOT NULL,
    breed VARCHAR(100),
    date_of_birth DATE,
    last_vaccination TIMESTAMP,
    medical_history JSON,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

#### appointments table
```sql
CREATE TABLE appointments (
    id UUID PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    service_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    notes TEXT,
    pet_id UUID NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,  -- ← This was missing
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

#### clinic_status table
```sql
CREATE TABLE clinic_status (
    id INTEGER PRIMARY KEY DEFAULT 1,
    status VARCHAR(20) DEFAULT 'open',
    updated_at TIMESTAMP NOT NULL
);
```

## Preventing Future Issues

### 1. Use Alembic for Migrations (Future Enhancement)

For production applications, consider using Alembic for database migrations:

```bash
pip install alembic
alembic init alembic
```

### 2. Version Control Your Schema

Keep track of schema changes in version control:
- Document all model changes
- Create migration scripts for each change
- Test migrations before deploying

### 3. Development Best Practices

When developing:
1. **Always run migrations** after pulling code changes
2. **Check model changes** in pull requests
3. **Test database operations** after schema changes
4. **Use database reset** freely in development

## Troubleshooting

### Migration Script Fails

**Error**: "Insufficient permissions"
```bash
# Solution: Check database user permissions
# Ensure your database user can ALTER tables
```

**Error**: "Existing appointments have no matching pets"
```bash
# Solution: Clean up orphaned appointments first
python -c "
from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    conn.execute(text('DELETE FROM appointments WHERE pet_id NOT IN (SELECT id FROM pets)'))
    conn.commit()
"
```

### Reset Script Fails

**Error**: "Cannot drop table because other objects depend on it"
```bash
# Solution: Use CASCADE
# The script already handles this, but if you're doing it manually:
DROP TABLE appointments CASCADE;
DROP TABLE pets CASCADE;
DROP TABLE users CASCADE;
DROP TABLE clinic_status CASCADE;
```

### After Migration, Still Getting Errors

1. **Restart the application:**
   ```bash
   # Stop the server (Ctrl+C)
   # Start it again
   uvicorn app.main:app --reload
   ```

2. **Check database connection:**
   ```bash
   python -c "from app.core.database import engine; print(engine.url)"
   ```

3. **Verify column exists:**
   ```bash
   python -c "
   from app.core.database import engine
   from sqlalchemy import text
   with engine.connect() as conn:
       result = conn.execute(text(\"SELECT column_name FROM information_schema.columns WHERE table_name='appointments'\"))
       print([row[0] for row in result])
   "
   ```

## Quick Reference

| Task | Command | Data Loss |
|------|---------|-----------|
| Add missing column | `python migrate_add_user_id.py` | No |
| Reset database | `python reset_database.py` | **YES** |
| Check schema | See "Verify column exists" above | No |
| Start server | `uvicorn app.main:app --reload` | No |

## Support

If you continue to have issues:

1. Check the error logs with `LOG_LEVEL=DEBUG`
2. Verify your `DATABASE_URL` in `.env`
3. Ensure PostgreSQL/NeonDB is accessible
4. Check that all models are imported in the migration scripts

---

**Last Updated**: February 8, 2024  
**Status**: ✅ Migration scripts ready to use
