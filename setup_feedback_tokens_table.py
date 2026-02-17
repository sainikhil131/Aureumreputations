#!/usr/bin/env python3
"""
Setup the feedback_tokens table in Supabase
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def setup_feedback_tokens_table():
    """Create the feedback_tokens table if it doesn't exist"""
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("🔧 Setting up feedback_tokens table...")
    
    try:
        # Try to create a test token to see if table exists
        test_result = supabase.table("feedback_tokens").select("*").limit(1).execute()
        print("✅ feedback_tokens table already exists!")
        
        # Show existing tokens
        if test_result.data:
            print(f"📊 Found {len(test_result.data)} existing tokens")
        else:
            print("📊 Table is empty (ready to use)")
            
    except Exception as e:
        error_msg = str(e).lower()
        
        if "relation" in error_msg and "does not exist" in error_msg:
            print("❌ feedback_tokens table does not exist")
            print("\n📋 Please create the table in Supabase with this SQL:")
            print("=" * 60)
            print("""
CREATE TABLE feedback_tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR(255) UNIQUE NOT NULL,
    business_id UUID NOT NULL,
    customer_name VARCHAR(255) DEFAULT '',
    expires_at BIGINT NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at BIGINT NOT NULL,
    FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE
);

-- Create index for faster token lookups
CREATE INDEX idx_feedback_tokens_token ON feedback_tokens(token);
CREATE INDEX idx_feedback_tokens_expires_at ON feedback_tokens(expires_at);
            """)
            print("=" * 60)
            print("\n🔗 Steps to create the table:")
            print("1. Go to your Supabase dashboard")
            print("2. Navigate to SQL Editor")
            print("3. Copy and paste the SQL above")
            print("4. Click 'Run' to execute")
            print("5. Run this script again to verify")
            
        else:
            print(f"❌ Error checking table: {str(e)}")

if __name__ == "__main__":
    setup_feedback_tokens_table()