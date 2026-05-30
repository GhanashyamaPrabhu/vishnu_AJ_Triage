#!/usr/bin/env python3
"""
Script to set up the database schema in Supabase and create the admin user.
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

def setup_database():
    """Set up the database schema and create admin user"""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
        sys.exit(1)
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("🔧 Setting up database schema...")
        
        # Create users table
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
        
        # Execute schema creation using RPC call
        try:
            result = supabase.rpc('exec_sql', {'sql': users_sql}).execute()
            print("✅ Users table created successfully")
        except Exception as e:
            print(f"⚠️  Users table may already exist: {e}")
        
        # Create admin user
        print("👤 Creating admin user...")
        admin_data = {
            "username": "ajadmin",
            "password_hash": hash_password("AJTriage2024!"),
            "role": "admin",
            "full_name": "AJ Admin",
            "is_active": True
        }
        
        # Check if admin user already exists
        try:
            existing_user = supabase.table("users").select("*").eq("username", "ajadmin").execute()
            
            if existing_user.data:
                print("Admin user 'ajadmin' already exists. Updating password...")
                # Update existing user
                result = supabase.table("users").update({
                    "password_hash": admin_data["password_hash"],
                    "role": "admin",
                    "full_name": "AJ Admin",
                    "is_active": True
                }).eq("username", "ajadmin").execute()
            else:
                print("Creating new admin user 'ajadmin'...")
                # Insert new user
                result = supabase.table("users").insert(admin_data).execute()
            
            if result.data:
                print("✅ Admin user created/updated successfully!")
                print("Username: ajadmin")
                print("Password: AJTriage2024!")
                print("Role: admin")
            else:
                print("❌ Failed to create/update admin user")
                print(f"Error: {result}")
                
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()