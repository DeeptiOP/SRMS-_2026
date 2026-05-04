#!/usr/bin/env python3
"""
SRMS Database Verification Script
==================================
This script verifies that the MySQL database is properly configured for SRMS.

Usage:
    python verify_database.py
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'srms_db'),
    'port': int(os.getenv('DB_PORT', '3306'))
}

class DatabaseVerifier:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.checks_passed = 0
        self.checks_failed = 0
        
    def connect(self):
        """Connect to the database"""
        try:
            self.conn = mysql.connector.connect(**db_config)
            self.cursor = self.conn.cursor(dictionary=True)
            return True
        except Error as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def check_table(self, table_name):
        """Check if a table exists"""
        try:
            self.cursor.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
            print(f"✅ Table '{table_name}' exists")
            self.checks_passed += 1
            return True
        except Error:
            print(f"❌ Table '{table_name}' missing or not accessible")
            self.checks_failed += 1
            return False
    
    def check_view(self, view_name):
        """Check if a view exists"""
        try:
            self.cursor.execute(f"SELECT 1 FROM {view_name} LIMIT 1")
            print(f"✅ View '{view_name}' exists")
            self.checks_passed += 1
            return True
        except Error:
            print(f"❌ View '{view_name}' missing or not accessible")
            self.checks_failed += 1
            return False
    
    def get_table_columns(self, table_name):
        """Get column information for a table"""
        try:
            self.cursor.execute(f"DESCRIBE {table_name}")
            columns = self.cursor.fetchall()
            return columns
        except Error as e:
            print(f"❌ Error getting columns for {table_name}: {e}")
            return []
    
    def get_table_row_count(self, table_name):
        """Get the number of rows in a table"""
        try:
            self.cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            result = self.cursor.fetchone()
            return result['count'] if result else 0
        except Error:
            return 0
    
    def verify_foreign_keys(self):
        """Verify foreign key relationships"""
        print("\n" + "="*60)
        print("🔗 FOREIGN KEY RELATIONSHIPS")
        print("="*60)
        
        fk_checks = {
            'class_subjects': [
                ('class_id references classes(id)', 'classes'),
                ('subject_id references subjects(id)', 'subjects')
            ],
            'marks': [
                ('users_id references users(id)', 'users'),
                ('subject_id references subjects(id)', 'subjects')
            ],
            'notices': [
                ('admin_id references users(id)', 'users')
            ]
        }
        
        for table, relationships in fk_checks.items():
            print(f"\n📦 Table: {table}")
            for desc, referenced_table in relationships:
                try:
                    # Check if data integrity is maintained
                    self.cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    result = self.cursor.fetchone()
                    if result and result['count'] > 0:
                        print(f"  ✅ {desc} - {result['count']} records")
                    else:
                        print(f"  ℹ️ {desc} - No data yet")
                    self.checks_passed += 1
                except Error as e:
                    print(f"  ❌ {desc} - Error: {e}")
                    self.checks_failed += 1
    
    def verify_indexes(self):
        """Verify that important indexes exist"""
        print("\n" + "="*60)
        print("🗂️  DATABASE INDEXES")
        print("="*60)
        
        indexes = {
            'users': ['idx_username', 'idx_email', 'idx_is_admin'],
            'marks': ['idx_users_id', 'idx_subject'],
            'classes': ['idx_department', 'idx_year'],
            'subjects': ['idx_subject_code'],
        }
        
        for table, expected_indexes in indexes.items():
            print(f"\n📑 Table: {table}")
            try:
                self.cursor.execute(f"SHOW INDEXES FROM {table}")
                existing_indexes = set()
                for index in self.cursor.fetchall():
                    existing_indexes.add(index['Key_name'])
                
                for idx in expected_indexes:
                    if idx in existing_indexes:
                        print(f"  ✅ Index '{idx}' exists")
                        self.checks_passed += 1
                    else:
                        print(f"  ⚠️  Index '{idx}' not found")
            except Error as e:
                print(f"  ❌ Error checking indexes: {e}")
                self.checks_failed += 1
    
    def run_verification(self):
        """Run all verification checks"""
        print("\n" + "="*60)
        print("🔍 SRMS DATABASE VERIFICATION")
        print("="*60)
        print(f"Host: {db_config['host']}")
        print(f"Database: {db_config['database']}")
        print(f"User: {db_config['user']}")
        print("="*60)
        
        if not self.connect():
            return False
        
        try:
            # Check if database exists
            try:
                self.cursor.execute("SELECT DATABASE()")
                db_name = self.cursor.fetchone()
                if db_name:
                    print(f"✅ Connected to database: {db_name.get('DATABASE()', 'unknown')}")
                    self.checks_passed += 1
            except Error:
                pass
            
            # Check tables
            print("\n" + "="*60)
            print("📋 TABLES")
            print("="*60)
            
            tables = ['users', 'classes', 'subjects', 'class_subjects', 'marks', 'notices']
            for table in tables:
                if self.check_table(table):
                    count = self.get_table_row_count(table)
                    print(f"   📊 {table}: {count} records")
            
            # Check views
            print("\n" + "="*60)
            print("👁️  DATABASE VIEWS")
            print("="*60)
            
            views = ['student_overview', 'class_performance', 'subject_performance']
            for view in views:
                self.check_view(view)
            
            # Verify foreign keys
            self.verify_foreign_keys()
            
            # Verify indexes
            self.verify_indexes()
            
            # Check user data
            print("\n" + "="*60)
            print("👥 USER ACCOUNTS")
            print("="*60)
            
            try:
                self.cursor.execute("SELECT COUNT(*) as admin_count FROM users WHERE is_admin=1")
                admin_count = self.cursor.fetchone()['admin_count']
                
                self.cursor.execute("SELECT COUNT(*) as student_count FROM users WHERE is_admin=0")
                student_count = self.cursor.fetchone()['student_count']
                
                print(f"✅ Admin accounts: {admin_count}")
                print(f"✅ Student accounts: {student_count}")
                
                if admin_count == 0:
                    print("\n⚠️  WARNING: No admin account found!")
                    print("   Run 'python init_admin.py' to create an admin account")
                
                self.checks_passed += 2
            except Error as e:
                print(f"❌ Error checking user data: {e}")
                self.checks_failed += 1
            
            # Display summary
            print("\n" + "="*60)
            print("📊 VERIFICATION SUMMARY")
            print("="*60)
            print(f"✅ Checks passed: {self.checks_passed}")
            print(f"❌ Checks failed: {self.checks_failed}")
            
            if self.checks_failed == 0:
                print("\n🎉 Database is properly configured!")
                return True
            else:
                print(f"\n⚠️  {self.checks_failed} checks failed. Please review the errors above.")
                return False
            
        except Error as e:
            print(f"❌ Verification error: {e}")
            return False
        finally:
            self.close()

def main():
    """Main function"""
    verifier = DatabaseVerifier()
    success = verifier.run_verification()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
