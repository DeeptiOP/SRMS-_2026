#!/usr/bin/env python3
"""
Initialize Admin User for SRMS
This script creates or updates the default admin user with the correct password hash
"""

import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'srms_db')
}

def initialize_admin():
    """Create or update admin user with correct password hash"""
    try:
        # Connect to database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Admin credentials
        admin_username = 'admin'
        admin_password = 'admin123'
        admin_email = 'admin@srms.com'
        
        # Generate password hash
        hashed_password = generate_password_hash(admin_password)
        
        print("=" * 60)
        print("SRMS ADMIN INITIALIZATION")
        print("=" * 60)
        print(f"Admin Username: {admin_username}")
        print(f"Admin Password: {admin_password}")
        print(f"Admin Email: {admin_email}")
        print(f"Password Hash: {hashed_password}")
        print("=" * 60)
        
        # Check if admin already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (admin_username,))
        admin_exists = cursor.fetchone()
        
        if admin_exists:
            # Update existing admin
            cursor.execute(
                "UPDATE users SET password = %s, email = %s, is_admin = 1 WHERE username = %s",
                (hashed_password, admin_email, admin_username)
            )
            print("✅ Admin user updated successfully!")
        else:
            # Create new admin
            cursor.execute(
                "INSERT INTO users (username, password, email, is_admin) VALUES (%s, %s, %s, %s)",
                (admin_username, hashed_password, admin_email, 1)
            )
            print("✅ Admin user created successfully!")
        
        conn.commit()
        
        # Verify
        cursor.execute("SELECT id, username, email, is_admin FROM users WHERE username = %s", (admin_username,))
        admin_user = cursor.fetchone()
        
        if admin_user:
            print("\n✅ Admin user verified:")
            print(f"   ID: {admin_user[0]}")
            print(f"   Username: {admin_user[1]}")
            print(f"   Email: {admin_user[2]}")
            print(f"   Is Admin: {admin_user[3]}")
            print("\n" + "=" * 60)
            print("✨ READY TO LOGIN!")
            print("=" * 60)
            print(f"Login URL: http://localhost:5000")
            print(f"Username: {admin_username}")
            print(f"Password: {admin_password}")
            print(f"Role: Admin")
            print("=" * 60)
        
        cursor.close()
        conn.close()
        
        return True
        
    except Error as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("\n🔐 Initializing SRMS Admin User...\n")
    success = initialize_admin()
    
    if not success:
        print("\n❌ Failed to initialize admin user!")
        print("Make sure:")
        print("   1. MySQL server is running")
        print("   2. Database 'srms_db' exists")
        print("   3. .env file has correct credentials")
        exit(1)
    else:
        print("\n✅ Admin initialization complete!")
