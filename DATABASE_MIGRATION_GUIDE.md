# Database Schema Migration - Content Library Columns

## 🐛 Problem

Database error: `column content.saved_to_library does not exist`

The backend code expects `saved_to_library` and `library_saved_at` columns in the `content` table, but they don't exist in the Render database.

---

## ✅ Solution: Run Database Migration

You have **3 options** to fix this:

---

## Option 1: Run Migration via Render Shell (RECOMMENDED)

This is the easiest way to update the production database on Render.

### Steps:

1. **Go to Render Dashboard:**
   - Visit: https://dashboard.render.com/
   - Navigate to your backend service

2. **Open Shell:**
   - Click on "Shell" tab
   - Wait for terminal to connect

3. **Run Migration Script:**
   ```bash
   python migrate_content_library.py
   ```

4. **Verify Success:**
   - Should see: ✅ Migration completed successfully!
   - Columns: saved_to_library, library_saved_at

5. **Test Your App:**
   - Refresh http://localhost:3000/dashboard/content
   - Error should be gone!

---

## Option 2: Run SQL Directly in Render Database

If you have access to the database directly:

1. **Connect to Render PostgreSQL:**
   - Go to your database in Render dashboard
   - Copy connection string

2. **Run Migration SQL:**
   ```sql
   -- Add saved_to_library column
   ALTER TABLE content 
   ADD COLUMN IF NOT EXISTS saved_to_library BOOLEAN NOT NULL DEFAULT FALSE;
   
   -- Add index
   CREATE INDEX IF NOT EXISTS ix_content_saved_to_library ON content(saved_to_library);
   
   -- Add library_saved_at column
   ALTER TABLE content 
   ADD COLUMN IF NOT EXISTS library_saved_at TIMESTAMP;
   
   -- Update existing records
   UPDATE content 
   SET saved_to_library = FALSE 
   WHERE saved_to_library IS NULL;
   ```

3. **Verify:**
   ```sql
   SELECT column_name, data_type 
   FROM information_schema.columns
   WHERE table_name = 'content' 
     AND column_name IN ('saved_to_library', 'library_saved_at');
   ```

---

## Option 3: Use Local Backend (For Testing)

If you want to test locally first:

1. **Start Local Backend:**
   ```bash
   cd backend
   source venv/bin/activate
   python migrate_content_library.py
   ```

2. **Update Frontend to Use Local:**
   ```bash
   # Edit frontend/.env.local
   NEXT_PUBLIC_API_URL=http://localhost:8003
   ```

3. **Test:**
   - Your local database will have the columns
   - App should work locally

4. **Still Need to Fix Render:**
   - Follow Option 1 or 2 to update Render database

---

## 📋 Migration Files Created

1. **`backend/migrations/add_content_library_columns.sql`**
   - Raw SQL migration script
   - Can be run directly in any PostgreSQL client

2. **`backend/migrate_content_library.py`**
   - Python script that runs the migration
   - Includes verification
   - Safe to run multiple times (uses IF NOT EXISTS)

---

## 🔍 What Gets Added

### Column 1: `saved_to_library`
- **Type:** BOOLEAN
- **Default:** FALSE
- **Nullable:** NOT NULL
- **Purpose:** Track if content is saved to library
- **Index:** Yes (for performance)

### Column 2: `library_saved_at`
- **Type:** TIMESTAMP
- **Default:** NULL
- **Nullable:** YES
- **Purpose:** Track when content was saved to library

---

## ⚠️ Important Notes

### Safe to Run Multiple Times
- Uses `IF NOT EXISTS` checks
- Won't create duplicate columns
- Won't fail if columns already exist

### No Data Loss
- Only adds columns
- Doesn't modify existing data
- Sets default values for new columns

### Backwards Compatible
- Existing content marked as `saved_to_library = FALSE`
- `library_saved_at` remains NULL for old content

---

## 🧪 Verification

After running migration, verify with:

```bash
# Via Render Shell:
python -c "
from app.db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT column_name, data_type 
        FROM information_schema.columns
        WHERE table_name = 'content' 
        AND column_name IN ('saved_to_library', 'library_saved_at')
    '''))
    for row in result:
        print(f'{row[0]}: {row[1]}')
"
```

Expected output:
```
saved_to_library: boolean
library_saved_at: timestamp without time zone
```

---

## 🚀 After Migration

1. **Refresh Your App:**
   - Go to http://localhost:3000/dashboard/content
   - Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

2. **Check Console:**
   - Should see no more database errors
   - Content should load successfully

3. **Test Features:**
   - ✅ View content list
   - ✅ Create new content
   - ✅ Save content to library (future feature)

---

## 💡 Why This Happened

The codebase was updated with Content Library feature columns, but the database schema wasn't migrated. This is common when:

- Code is deployed but migrations aren't run
- Database schema gets out of sync with code
- New features are added that require schema changes

**Going forward:** Always run migrations after pulling new code!

---

## 🆘 If Migration Fails

### Error: "permission denied for table content"
**Solution:** Need database admin access. Contact whoever manages the Render database.

### Error: "relation content does not exist"
**Solution:** Main content table is missing. Bigger issue - may need to recreate database.

### Error: "column already exists"
**Solution:** Migration already ran! Columns exist. Just refresh your app.

---

## 📞 Need Help?

If you get stuck:
1. Check Render logs for detailed error messages
2. Verify database connection works
3. Check if columns already exist (might be a caching issue)

---

**Ready to fix?** Follow **Option 1** above - it's the easiest! 🚀
