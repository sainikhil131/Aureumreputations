#!/usr/bin/env python3
"""
Update the feedback_tokens table to support 2-minute expiry after opening
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def update_feedback_tokens_schema():
    """Add new fields to support expiry after opening"""
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("🔧 Updating feedback_tokens table schema...")
    
    try:
        # Check if new columns already exist
        result = supabase.table("feedback_tokens").select("*").limit(1).execute()
        
        if result.data and len(result.data) > 0:
            existing_columns = result.data[0].keys()
            print(f"📊 Current columns: {list(existing_columns)}")
            
            # Check if we need to add new columns
            needs_update = False
            if 'first_opened_at' not in existing_columns:
                needs_update = True
            if 'opened_expires_at' not in existing_columns:
                needs_update = True
            if 'short_code' not in existing_columns:
                needs_update = True
                
            if needs_update:
                print("\n📋 Please run this SQL in Supabase to add new columns:")
                print("=" * 60)
                print("""
-- Add new columns for tracking when link is first opened
ALTER TABLE feedback_tokens 
ADD COLUMN IF NOT EXISTS first_opened_at BIGINT DEFAULT NULL,
ADD COLUMN IF NOT EXISTS opened_expires_at BIGINT DEFAULT NULL,
ADD COLUMN IF NOT EXISTS short_code VARCHAR(10) DEFAULT NULL;

-- Create index for short_code lookups
CREATE INDEX IF NOT EXISTS idx_feedback_tokens_short_code ON feedback_tokens(short_code);
CREATE INDEX IF NOT EXISTS idx_feedback_tokens_first_opened ON feedback_tokens(first_opened_at);

-- Update existing tokens to have short codes
UPDATE feedback_tokens 
SET short_code = UPPER(SUBSTRING(MD5(RANDOM()::text), 1, 6))
WHERE short_code IS NULL;

-- Make short_code unique
ALTER TABLE feedback_tokens ADD CONSTRAINT unique_short_code UNIQUE (short_code);
                """)
                print("=" * 60)
                print("\n🔗 Steps to update the table:")
                print("1. Go to your Supabase dashboard")
                print("2. Navigate to SQL Editor")
                print("3. Copy and paste the SQL above")
                print("4. Click 'Run' to execute")
                print("5. Run this script again to verify")
            else:
                print("✅ Schema is already up to date!")
        else:
            print("📊 Table is empty, schema update needed")
            
    except Exception as e:
        print(f"❌ Error checking table: {str(e)}")

if __name__ == "__main__":
    update_feedback_tokens_schema()