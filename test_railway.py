#!/usr/bin/env python3
"""
Verify Railway database connection for SRMS
"""

import mysql.connector
import os
from dotenv import load_dotenv

def test_railway_connection():
    """Test Railway database connection"""
    load_dotenv()

    print("🔍 Testing Railway Database Connection")
    print("=" * 50)

    # Current local config
    print("📄 Local .env configuration:")
    print(f"   DB_HOST: {os.getenv('DB_HOST')}")
    print(f"   DB_PORT: {os.getenv('DB_PORT')}")
    print(f"   DB_USER: {os.getenv('DB_USER')}")
    print(f"   DB_NAME: {os.getenv('DB_NAME')}")
    print()

    # Test external connection (for local testing)
    print("🌐 Testing EXTERNAL connection (junction.proxy.rlwy.net:37430)...")
    try:
        conn = mysql.connector.connect(
            host='junction.proxy.rlwy.net',
            port=37430,
            user='root',
            password='QJAklEaRgLuequxVOlMGRUKwZGCcMIwa',
            database='railway',
            connection_timeout=10
        )
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        print(f"   ✅ External connection works! Users: {count}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"   ❌ External connection failed: {str(e)[:100]}...")

    print()
    print("🏭 What Render needs (INTERNAL connection):")
    print("   DB_HOST=mysql.railway.internal")
    print("   DB_PORT=3306")
    print("   DB_USER=root")
    print("   DB_PASSWORD=QJAklEaRgLuequxVOlMGRUKwZGCcMIwa")
    print("   DB_NAME=railway")
    print()
    print("⚠️  IMPORTANT: Set these in Render dashboard, NOT in .env file!")
    print("   Render uses INTERNAL Railway connection (mysql.railway.internal)")
    print("   Local uses EXTERNAL Railway connection (junction.proxy.rlwy.net)")

if __name__ == "__main__":
    test_railway_connection()