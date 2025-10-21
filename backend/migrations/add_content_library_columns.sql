-- Migration: Add Content Library columns to content and published_posts tables
-- Date: October 21, 2025
-- Description: Adds saved_to_library and library_saved_at columns for content library feature

-- ============================================
-- CONTENT TABLE
-- ============================================

-- Add saved_to_library column
ALTER TABLE content 
ADD COLUMN IF NOT EXISTS saved_to_library BOOLEAN NOT NULL DEFAULT FALSE;

-- Add index on saved_to_library for performance
CREATE INDEX IF NOT EXISTS ix_content_saved_to_library ON content(saved_to_library);

-- Add library_saved_at column
ALTER TABLE content 
ADD COLUMN IF NOT EXISTS library_saved_at TIMESTAMP;

-- Update existing records (optional: mark existing content as not saved to library)
UPDATE content 
SET saved_to_library = FALSE 
WHERE saved_to_library IS NULL;

-- ============================================
-- PUBLISHED_POSTS TABLE
-- ============================================

-- Add saved_to_library column
ALTER TABLE published_posts 
ADD COLUMN IF NOT EXISTS saved_to_library BOOLEAN NOT NULL DEFAULT FALSE;

-- Add index on saved_to_library for performance
CREATE INDEX IF NOT EXISTS ix_published_posts_saved_to_library ON published_posts(saved_to_library);

-- Add library_saved_at column
ALTER TABLE published_posts 
ADD COLUMN IF NOT EXISTS library_saved_at TIMESTAMP;

-- Update existing records (optional: mark existing posts as not saved to library)
UPDATE published_posts 
SET saved_to_library = FALSE 
WHERE saved_to_library IS NULL;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Verify content table
SELECT 'content' as table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'content' 
  AND column_name IN ('saved_to_library', 'library_saved_at')
ORDER BY ordinal_position;

-- Verify published_posts table
SELECT 'published_posts' as table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'published_posts' 
  AND column_name IN ('saved_to_library', 'library_saved_at')
ORDER BY ordinal_position;
