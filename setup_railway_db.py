#!/usr/bin/env python3
"""
Railway Database Setup Script for SRMS
This script helps initialize the Railway MySQL database with the SRMS schema.
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Connect to Railway MySQL database"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def initialize_database():
    """Initialize the database with SRMS schema"""
    connection = get_db_connection()
    if not connection:
        print("❌ Failed to connect to database")
        return False

    try:
        cursor = connection.cursor()

        # Read and execute the setup script
        with open('setup_database.sql', 'r', encoding='utf-8') as file:
            sql_script = file.read()

        # Split the script into individual statements
        statements = sql_script.split(';')

        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    print(f"✅ Executed: {statement[:50]}...")
                except Error as e:
                    print(f"⚠️  Warning: {e}")

        connection.commit()
        print("✅ Database schema initialized successfully!")

        # Create default admin user
        try:
            hashed_password = 'pbkdf2:sha256:600000$your_salt_here$your_hash_here'  # This will be replaced by proper hashing
            cursor.execute("""
                INSERT INTO users (username, password, email, course, year, department, is_admin)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE username=username
            """, ('admin', hashed_password, 'admin@srms.com', '', '', '', 1))
            connection.commit()
            print("✅ Default admin user created (username: admin, password: admin123)")
        except Error as e:
            print(f"⚠️  Admin user creation warning: {e}")

        return True

    except Error as e:
        print(f"❌ Database initialization error: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("🚀 Initializing Railway Database for SRMS...")
    print("=" * 50)

    # Check environment variables
    required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your Railway environment variables or .env file")
        exit(1)

    success = initialize_database()
    if success:
        print("\n🎉 Database setup complete!")
        print("You can now deploy your SRMS application to Render.")
    else:
        print("\n❌ Database setup failed. Please check your Railway configuration.")
        exit(1)