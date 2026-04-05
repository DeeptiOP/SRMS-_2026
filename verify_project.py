#!/usr/bin/env python3
"""
SRMS Verification & Completeness Check Script
This script verifies that all components of SRMS are properly implemented
"""

import os
import sys
from pathlib import Path

def check_files():
    """Check if all required files exist"""
    print("\n" + "="*70)
    print("📋 CHECKING PROJECT FILES")
    print("="*70)
    
    base_path = Path(__file__).parent
    
    # Required files
    required_files = {
        'Core': [
            'app.py',
            'init_admin.py',
            'setup_database.sql',
            'requirements.txt',
            '.env'
        ],
        'Documentation': [
            'INDEX.md',
            'QUICK_START_GUIDE.md',
            'IMPLEMENTATION_GUIDE.md',
            'CHANGES_SUMMARY.md',
            'FEATURE_MATRIX.md',
            'README.md'
        ],
        'Configuration': [
            '.env.example'
        ]
    }
    
    all_found = True
    
    for category, files in required_files.items():
        print(f"\n{category}:")
        for file in files:
            file_path = base_path / file
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"  ✅ {file} ({size} bytes)")
            else:
                print(f"  ❌ {file} (NOT FOUND)")
                all_found = False
    
    return all_found

def check_templates():
    """Check if all templates exist"""
    print("\n" + "="*70)
    print("📄 CHECKING TEMPLATES")
    print("="*70)
    
    base_path = Path(__file__).parent / 'templates'
    
    required_templates = [
        # Authentication
        'index.html',
        'register.html',
        'admin_register.html',
        'change_password.html',
        
        # Admin Pages
        'admin.html',
        'classes.html',
        'subjects.html',
        'class_subjects.html',
        'marks.html',
        'edit_student.html',
        'add_notice.html',
        
        # Student Pages
        'dashboard.html',
        'profile.html',
        'notices.html',
        'search_result.html',
        
        # Error Pages
        '404.html',
        '500.html'
    ]
    
    all_found = True
    
    for template in required_templates:
        template_path = base_path / template
        if template_path.exists():
            size = template_path.stat().st_size
            print(f"  ✅ {template} ({size} bytes)")
        else:
            print(f"  ❌ {template} (NOT FOUND)")
            all_found = False
    
    return all_found

def check_static():
    """Check if all static files exist"""
    print("\n" + "="*70)
    print("🎨 CHECKING STATIC FILES")
    print("="*70)
    
    base_path = Path(__file__).parent / 'static'
    
    required_static = [
        'styles.css',
        'admin.css',
        'dashboard.css',
        'marks.css'
    ]
    
    all_found = True
    
    for static_file in required_static:
        static_path = base_path / static_file
        if static_path.exists():
            size = static_path.stat().st_size
            print(f"  ✅ {static_file} ({size} bytes)")
        else:
            print(f"  ❌ {static_file} (NOT FOUND)")
            all_found = False
    
    return all_found

def check_python_syntax():
    """Check Python files for syntax errors"""
    print("\n" + "="*70)
    print("🐍 CHECKING PYTHON SYNTAX")
    print("="*70)
    
    base_path = Path(__file__).parent
    python_files = ['app.py', 'init_admin.py']
    
    all_valid = True
    
    for py_file in python_files:
        file_path = base_path / py_file
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), py_file, 'exec')
            print(f"  ✅ {py_file} (Valid syntax)")
        except SyntaxError as e:
            print(f"  ❌ {py_file} (Syntax error: {e})")
            all_valid = False
        except Exception as e:
            print(f"  ❌ {py_file} (Error: {e})")
            all_valid = False
    
    return all_valid

def check_database_schema():
    """Check if database schema file is complete"""
    print("\n" + "="*70)
    print("🗄️  CHECKING DATABASE SCHEMA")
    print("="*70)
    
    base_path = Path(__file__).parent / 'setup_database.sql'
    
    if not base_path.exists():
        print("  ❌ setup_database.sql not found")
        return False
    
    with open(base_path, 'r') as f:
        content = f.read()
    
    # Check for required tables
    required_tables = [
        'CREATE TABLE.*users',
        'CREATE TABLE.*classes',
        'CREATE TABLE.*subjects',
        'CREATE TABLE.*class_subjects',
        'CREATE TABLE.*marks',
        'CREATE TABLE.*notices'
    ]
    
    import re
    all_found = True
    
    for table in required_tables:
        if re.search(table, content):
            table_name = table.split('.*')[1]
            print(f"  ✅ {table_name} table defined")
        else:
            print(f"  ❌ {table.split('.*')[1]} table not found")
            all_found = False
    
    return all_found

def check_routes():
    """Check if all required routes are present in app.py"""
    print("\n" + "="*70)
    print("🛣️  CHECKING API ROUTES")
    print("="*70)
    
    base_path = Path(__file__).parent / 'app.py'
    
    with open(base_path, 'r') as f:
        content = f.read()
    
    required_routes = [
        '/@app.route.*/',
        '/@app.route.*index',
        '/@app.route.*dashboard',
        '/@app.route.*register',
        '/@app.route.*admin',
        '/@app.route.*marks',
        '/@app.route.*classes',
        '/@app.route.*subjects',
        '/@app.route.*class_subjects',
        '/@app.route.*notices',
        '/@app.route.*add_notice',
        '/@app.route.*edit_student',
        '/@app.route.*change_password',
        '/@app.route.*search_result',
        '/@app.route.*profile',
        '/@app.route.*logout',
    ]
    
    import re
    all_found = True
    
    for route in required_routes:
        if re.search(route, content):
            route_name = route.split('.*')[1] if '.*' in route else route
            print(f"  ✅ {route_name} route implemented")
        else:
            print(f"  ❌ {route} route not found")
            all_found = False
    
    return all_found

def check_requirements():
    """Check requirements.txt"""
    print("\n" + "="*70)
    print("📦 CHECKING DEPENDENCIES")
    print("="*70)
    
    base_path = Path(__file__).parent / 'requirements.txt'
    
    if not base_path.exists():
        print("  ❌ requirements.txt not found")
        return False
    
    required_packages = [
        'Flask',
        'mysql-connector-python',
        'Werkzeug',
        'python-dotenv'
    ]
    
    with open(base_path, 'r') as f:
        content = f.read()
    
    all_found = True
    
    for package in required_packages:
        if package in content:
            print(f"  ✅ {package} listed")
        else:
            print(f"  ❌ {package} not found")
            all_found = False
    
    return all_found

def main():
    """Run all checks"""
    print("\n" + "🔍 SRMS COMPLETENESS VERIFICATION")
    print("Starting comprehensive project check...\n")
    
    results = {
        'Files': check_files(),
        'Templates': check_templates(),
        'Static Assets': check_static(),
        'Python Syntax': check_python_syntax(),
        'Database Schema': check_database_schema(),
        'API Routes': check_routes(),
        'Dependencies': check_requirements()
    }
    
    # Summary
    print("\n" + "="*70)
    print("📊 VERIFICATION SUMMARY")
    print("="*70)
    
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    
    for component, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {component:<25} {status}")
    
    print(f"\n  Total: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("\n" + "="*70)
        print("✨ ALL CHECKS PASSED! Project is complete and ready! ✨")
        print("="*70)
        print("\nNext steps:")
        print("  1. Run: mysql -u root -p < setup_database.sql")
        print("  2. Run: python init_admin.py")
        print("  3. Run: pip install -r requirements.txt")
        print("  4. Run: python app.py")
        print("\nThen open: http://localhost:5000")
        return 0
    else:
        print("\n" + "="*70)
        print("⚠️  Some checks failed. Please review the issues above.")
        print("="*70)
        return 1

if __name__ == '__main__':
    sys.exit(main())
