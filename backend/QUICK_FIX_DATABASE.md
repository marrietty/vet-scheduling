# Quick Fix: Database Schema Issue

## 🔴 Error You're Seeing

```
psycopg2.errors.UndefinedColumn: column appointments.user_id does not exist
```

## ✅ Quick Fix (Choose One)

### Option A: Migration (Keeps Your Data) ⭐ Recommended

```bash
cd backend
python migrate_add_user_id.py
```

Then restart your server:
```bash
uvicorn app.main:app --reload
```

### Option B: Reset Database (Deletes Everything)

```bash
cd backend
python reset_database.py
```

Then restart your server:
```bash
uvicorn app.main:app --reload
```

## 📋 What Happened?

The `appointments` table in your database is missing the `user_id` column that the application code expects. This happens when:
- Database was created with an older version of the code
- Migrations weren't run after code updates
- Database schema got out of sync

## 🎯 Which Option Should I Choose?

| Situation | Use This | Why |
|-----------|----------|-----|
| I have important data | **Option A** (Migration) | Preserves all users, pets, appointments |
| I'm just testing/developing | **Option B** (Reset) | Faster, cleaner start |
| I'm not sure | **Option A** (Migration) | Safer choice |

## ✅ How to Verify It's Fixed

After running the migration and restarting:

1. Try the operation that failed (e.g., delete a pet)
2. Check the logs - no more `user_id does not exist` errors
3. Test creating/viewing appointments

## 📚 More Information

See `DATABASE_MANAGEMENT.md` for:
- Detailed explanation
- Troubleshooting steps
- Database schema reference
- Prevention tips

---

**TL;DR**: Run `python migrate_add_user_id.py` then restart your server. Done! ✅
