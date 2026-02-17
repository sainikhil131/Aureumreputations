#!/usr/bin/env python3
"""
Setup script to create the clients table in Supabase database
Run this script once to set up the client authentication system
"""

from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_clients_table():
    """Create the clients table for client authentication"""
    
    # SQL to create clients table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS clients (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_temporary_password BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_clients_email ON clients(email);
    CREATE INDEX IF NOT EXISTS idx_clients_business_id ON clients(business_id);
    
    -- Add RLS (Row Level Security) policies if needed
    ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
    """
    
    try:
        # Execute the SQL using Supabase's rpc function or direct SQL execution
        print("Creating clients table...")
        
        # Note: This is a simplified approach. In production, you might want to use migrations
        # For now, we'll create the table manually in Supabase dashboard or use SQL editor
        
        print("✅ Please run the following SQL in your Supabase SQL editor:")
        print("=" * 60)
        print(create_table_sql)
        print("=" * 60)
        print("\nAlternatively, you can create the table manually with these columns:")
        print("- id (uuid, primary key, default gen_random_uuid())")
        print("- business_id (uuid, foreign key to businesses.id)")
        print("- email (text, unique)")
        print("- password_hash (text)")
        print("- is_temporary_password (bool, default true)")
        print("- created_at (timestamptz, default now())")
        print("- updated_at (timestamptz, default now())")
        
        return True
        
    except Exception as e:
        print(f"Error creating clients table: {str(e)}")
        return False

def test_database_connection():
    """Test the database connection"""
    try:
        # Test connection by querying businesses table
        result = supabase.table("businesses").select("id").limit(1).execute()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up Client Authentication System")
    print("=" * 50)
    
    # Test database connection
    if not test_database_connection():
        print("Please check your Supabase configuration in .env file")
        exit(1)
    
    # Create clients table
    create_clients_table()
    
    print("\n🎉 Setup instructions provided above!")
    print("After creating the table, you can:")
    print("1. Run the Flask app: python app.py")
    print("2. Login as admin: /login (admin/admin123)")
    print("3. Create client accounts: /admin/create-client")
    print("4. Clients can login at: /login (using their email)")