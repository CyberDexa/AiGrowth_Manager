-- Migration: Add Content Library columns to content table
-- Date: October 21, 2025
-- Description: Adds saved_to_library and library_saved_at columns for content library feature

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

-- Verification query
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'content' 
  AND column_name IN ('saved_to_library', 'library_saved_at')
ORDER BY ordinal_position;
