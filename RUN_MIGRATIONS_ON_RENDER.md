# How to Run Database Migrations on Render

## Problem
The `images` table (and possibly other tables) don't exist in your Render database because migrations haven't been run.

## Solution Options

### Option 1: Run Migrations via Render Shell (Recommended)

1. **Go to your Render Dashboard**
   - Visit https://dashboard.render.com
   - Select your `ai-growth-manager` service

2. **Open the Shell**
   - Click on the "Shell" tab
   - This opens a terminal connected to your running service

3. **Run the migration command:**
   ```bash
   alembic upgrade head
   ```

4. **Verify success:**
   - You should see output showing which migrations were applied
   - Look for: "Running upgrade ... -> 8aedf3a5c925, add_images_table"

---

### Option 2: Add Migration to Build Command

This ensures migrations run automatically on every deployment.

1. **Go to Render Dashboard** → Your Service → Settings

2. **Update the Build Command** to:
   ```bash
   pip install -r requirements.txt && alembic upgrade head
   ```

3. **Save and Redeploy**

**Note:** This only works if your database is accessible during the build phase.

---

### Option 3: Create a Manual Deploy Hook

If you can't access the shell, you can trigger migrations via a one-time job:

1. **In Render Dashboard**, create a new **Cron Job** or **One-off Job**

2. **Set the command to:**
   ```bash
   alembic upgrade head
   ```

3. **Use the same environment variables** as your main service

4. **Run it once** to apply migrations

---

## Verification

After running migrations, test the images endpoint:

```bash
curl https://ai-growth-manager.onrender.com/api/v1/images?business_id=1
```

You should get a response (even if empty) instead of a database error.

---

## List of Migrations That Need to Run

Based on your codebase, these migrations should exist:

1. ✅ Initial tables (businesses, users, social_accounts, etc.)
2. ✅ Add images table (8aedf3a5c925) - **THIS IS MISSING**
3. ✅ Add published_posts table
4. ✅ Add analytics tables
5. ✅ Add content_templates table
6. ✅ Add scheduled_posts table

Check which migrations have been applied:

```bash
# In Render Shell
alembic current
```

Check which migrations are available:

```bash
# In Render Shell
alembic history
```

---

## Troubleshooting

### Error: "relation already exists"
Some migrations may have partially run. You can:
```bash
# Mark specific migration as complete without running it
alembic stamp 8aedf3a5c925
```

### Error: "database is locked"
Your service might be running. Temporarily stop it, run migrations, then restart.

### Can't Access Shell
Contact Render support or use Option 2 to add migrations to build command.

---

## Quick Fix (If All Else Fails)

If you can't run Alembic migrations, you can manually create the images table via SQL:

1. **Connect to your Render database** (get connection string from Render dashboard)

2. **Run this SQL:**

```sql
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    business_id INTEGER NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    storage_provider VARCHAR(20) NOT NULL,
    storage_url TEXT NOT NULL,
    cloudinary_public_id VARCHAR(255),
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(50) NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    ai_generated BOOLEAN NOT NULL DEFAULT false,
    ai_prompt TEXT,
    ai_model VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE
);

CREATE INDEX ix_images_id ON images(id);
CREATE INDEX ix_images_business_id ON images(business_id);
CREATE INDEX ix_images_created_at ON images(created_at);
```

3. **Mark the migration as applied:**
```bash
alembic stamp 8aedf3a5c925
```

---

**After running migrations, your image upload should work!** ✅
