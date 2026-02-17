#!/usr/bin/env python3
"""
Script to fix Row Level Security (RLS) policies for the clients table
Run this after creating the clients table to allow proper access
"""

def print_rls_fix_sql():
    """Print the SQL needed to fix RLS policies"""
    
    rls_fix_sql = """
-- Disable RLS temporarily for easier management (you can re-enable later if needed)
ALTER TABLE clients DISABLE ROW LEVEL SECURITY;

-- OR if you want to keep RLS enabled, create policies that allow access:
-- ALTER TABLE clients ENABLE ROW LEVEL SECURITY;

-- Policy to allow service role (your app) to do everything
-- CREATE POLICY "Service role can manage clients" ON clients
-- FOR ALL USING (true) WITH CHECK (true);

-- Policy to allow authenticated users to read their own data
-- CREATE POLICY "Users can read own client data" ON clients
-- FOR SELECT USING (auth.uid()::text = id::text);

-- Policy to allow inserts (for creating new clients)
-- CREATE POLICY "Allow client creation" ON clients
-- FOR INSERT WITH CHECK (true);

-- Policy to allow updates (for password changes)
-- CREATE POLICY "Allow client updates" ON clients
-- FOR UPDATE USING (true) WITH CHECK (true);
"""
    
    print("🔧 RLS Policy Fix for Clients Table")
    print("=" * 50)
    print("The clients table has RLS enabled but no policies set up.")
    print("This prevents your app from accessing the table.")
    print("\n✅ Run this SQL in your Supabase SQL editor:")
    print("=" * 60)
    print(rls_fix_sql)
    print("=" * 60)
    print("\n📝 Recommendation:")
    print("For simplicity, disable RLS on the clients table since your app")
    print("handles authentication and authorization at the application level.")
    print("\nIf you need RLS for additional security, you can create specific")
    print("policies based on your requirements.")

if __name__ == "__main__":
    print_rls_fix_sql()