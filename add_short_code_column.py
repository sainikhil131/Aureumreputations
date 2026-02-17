#!/usr/bin/env python3
"""
Database migration script to add short_code column to feedback_tokens table
Run this once to update your existing database schema
"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def add_short_code_column():
    """Add short_code column to feedback_tokens table"""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("🔄 Testing database connection...")
        
        # Test the connection by trying to read from the table
        result = supabase.table("feedback_tokens").select("*").limit(1).execute()
        print("✅ Database connection successful")
        
        print("\n📝 Please run the following SQL commands in your Supabase SQL Editor:")
        print("=" * 60)
        print("ALTER TABLE feedback_tokens ADD COLUMN IF NOT EXISTS short_code VARCHAR(6) UNIQUE;")
        print("CREATE INDEX IF NOT EXISTS idx_feedback_tokens_short_code ON feedback_tokens(short_code);")
        print("=" * 60)
        
        print("\n📍 How to run this SQL:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to 'SQL Editor'")
        print("3. Copy and paste the SQL commands above")
        print("4. Click 'Run' to execute")
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to database: {str(e)}")
        print("\n📝 Manual SQL to run in Supabase SQL Editor:")
        print("ALTER TABLE feedback_tokens ADD COLUMN IF NOT EXISTS short_code VARCHAR(6) UNIQUE;")
        print("CREATE INDEX IF NOT EXISTS idx_feedback_tokens_short_code ON feedback_tokens(short_code);")
        return False

if __name__ == "__main__":
    print("🔄 Preparing to add short_code column to feedback_tokens table...")
    success = add_short_code_column()
    
    if success:
        print("\n🎉 Database connection verified!")
        print("After running the SQL commands, your feedback links will be much shorter:")
        print("\nExample transformation:")
        print("Before: https://yourdomain.com/feedback/d5439584-89bd-4406-84e0-dc6979a56e52?token=lXQ-yhcx4cw2AQcMPGug4rVTAOALMXFkgeEMOvlM-xs")
        print("After:  https://yourdomain.com/r/Abc123")
        print("\n✨ Much more professional and easier to share!")
    else:
        print("\n⚠️  Please check your database connection and run the SQL manually.")