#!/usr/bin/env python3
"""
Script to create the default admin user in Supabase database.
"""

import os
import sys
import hashlib
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv(dotenv_path="../.env")

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin_user():
    """Create the default admin user in Supabase"""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
        sys.exit(1)
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # First, create the users table if it doesn't exist
        print("🔧 Creating users table if it doesn't exist...")
        users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            role VARCHAR(20) NOT NULL CHECK (role IN ('triage_nurse', 'consultant', 'admin')),
            department VARCHAR(50) DEFAULT 'Department of Paediatrics',
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Use direct SQL execution
        try:
            # Try to create table using SQL
            supabase.postgrest.session.post(
                f"{supabase_url}/rpc/exec_sql",
                json={"sql": users_sql},
                headers={"apikey": supabase_key, "Authorization": f"Bearer {supabase_key}"}
            )
            print("✅ Users table ready")
        except Exception as table_error:
            print(f"⚠️  Table creation note: {table_error}")
        
        # Admin user details
        admin_data = {
            "username": "ajadmin",
            "password_hash": hash_password("AJTriage2024!"),
            "role": "admin",
            "full_name": "AJ Admin",
            "is_active": True
        }
        
        print("👤 Creating admin user...")
        
        # Try to insert directly first
        try:
            result = supabase.table("users").insert(admin_data).execute()
            print("✅ Admin user created successfully!")
            print("Username: ajadmin")
            print("Password: AJTriage2024!")
            print("Role: admin")
        except Exception as insert_error:
            # If insert fails, try to update existing user
            print(f"User may exist, trying to update: {insert_error}")
            try:
                result = supabase.table("users").update({
                    "password_hash": admin_data["password_hash"],
                    "role": "admin",
                    "full_name": "AJ Admin",
                    "is_active": True
                }).eq("username", "ajadmin").execute()
                print("✅ Admin user updated successfully!")
                print("Username: ajadmin")
                print("Password: AJTriage2024!")
                print("Role: admin")
            except Exception as update_error:
                print(f"❌ Failed to create/update admin user: {update_error}")
            
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_admin_user()