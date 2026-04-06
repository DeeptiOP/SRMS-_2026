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
        # Use Railway internal connection for Railway services
        # For local development, use the public URL
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'mysql.railway.internal'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'QJAklEaRgLuequxVOlMGRUKwZGCcMIwa'),
            database=os.getenv('DB_NAME', 'railway'),
            port=int(os.getenv('DB_PORT', '3306'))
        )
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        print("If connecting from local machine, try using the Railway public URL:")
        print("Set DB_HOST=junction.proxy.rlwy.net and DB_PORT=37430 in your .env file")
        return None

def initialize_database():
    """Initialize the database with SRMS schema"""
    connection = get_db_connection()
    if not connection:
        print("❌ Failed to connect to database")
        return False

    try:
        cursor = connection.cursor()

        # Create tables directly (not using the SQL file that has wrong database name)
        print("🏗️  Creating SRMS tables...")

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                roll_number VARCHAR(50),
                course VARCHAR(100),
                year VARCHAR(50),
                department VARCHAR(100),
                is_admin INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_email (email),
                INDEX idx_is_admin (is_admin),
                INDEX idx_roll_number (roll_number),
                INDEX idx_department (department)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✅ Users table created")

        # Classes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id INT PRIMARY KEY AUTO_INCREMENT,
                class_name VARCHAR(100) NOT NULL,
                description TEXT,
                year VARCHAR(50),
                department VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_class_name (class_name),
                INDEX idx_year (year),
                INDEX idx_department (department)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✅ Classes table created")

        # Subjects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INT PRIMARY KEY AUTO_INCREMENT,
                subject_name VARCHAR(100) NOT NULL,
                subject_code VARCHAR(50),
                description TEXT,
                credits DECIMAL(3,1),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_subject_name (subject_name),
                UNIQUE KEY unique_subject_code (subject_code),
                INDEX idx_subject_code (subject_code)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✅ Subjects table created")

        # Class-Subjects junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS class_subjects (
                id INT PRIMARY KEY AUTO_INCREMENT,
                class_id INT NOT NULL,
                subject_id INT NOT NULL,
                is_active INT DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
                UNIQUE KEY unique_class_subject (class_id, subject_id),
                INDEX idx_class_id (class_id),
                INDEX idx_subject_id (subject_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✅ Class-Subjects table created")

        # Marks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS marks (
                id INT PRIMARY KEY AUTO_INCREMENT,
                users_id INT NOT NULL,
                subject_id INT,
                subject VARCHAR(100) NOT NULL,
                department VARCHAR(100),
                marks INT NOT NULL CHECK (marks >= 0 AND marks <= 100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (users_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL,
                UNIQUE KEY unique_student_subject (users_id, subject),
                INDEX idx_users_id (users_id),
                INDEX idx_subject (subject),
                INDEX idx_marks (marks)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✅ Marks table created")

        # Notices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notices (
                id INT PRIMARY KEY AUTO_INCREMENT,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                admin_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE SET NULL,
                INDEX idx_admin_id (admin_id),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✅ Notices table created")

        # Insert sample data
        print("📝 Inserting sample data...")

        # Classes
        classes_data = [
            ('CSE-A', 'Computer Science Engineering - Section A', '2nd Year', 'Computer Science'),
            ('CSE-B', 'Computer Science Engineering - Section B', '2nd Year', 'Computer Science'),
            ('ECE-A', 'Electronics and Communication Engineering - Section A', '2nd Year', 'Electronics'),
            ('ECE-B', 'Electronics and Communication Engineering - Section B', '2nd Year', 'Electronics'),
            ('MECH-A', 'Mechanical Engineering - Section A', '2nd Year', 'Mechanical'),
            ('IT-A', 'Information Technology - Section A', '2nd Year', 'Information Technology')
        ]

        cursor.executemany("""
            INSERT IGNORE INTO classes (class_name, description, year, department)
            VALUES (%s, %s, %s, %s)
        """, classes_data)
        print("✅ Classes data inserted")

        # Subjects
        subjects_data = [
            ('Data Structures', 'CS201', 'Study of data structures and algorithms', 4.0),
            ('Database Management', 'CS202', 'Relational database design and SQL', 4.0),
            ('Web Development', 'CS203', 'Frontend and backend web development', 4.0),
            ('OOPS with Java', 'CS204', 'Object-oriented programming concepts', 4.0),
            ('Digital Logic Design', 'EC201', 'Boolean algebra and logic circuits', 3.0),
            ('Signals and Systems', 'EC202', 'Analog and digital signal processing', 4.0),
            ('Thermodynamics', 'ME201', 'Laws of thermodynamics and applications', 4.0),
            ('Fluid Mechanics', 'ME202', 'Study of fluid flow characteristics', 4.0),
            ('Mathematics III', 'MA301', 'Calculus and Differential Equations', 4.0),
            ('Physics II', 'PH301', 'Electromagnetic theory and optics', 4.0)
        ]

        cursor.executemany("""
            INSERT IGNORE INTO subjects (subject_name, subject_code, description, credits)
            VALUES (%s, %s, %s, %s)
        """, subjects_data)
        print("✅ Subjects data inserted")

        # Class-Subject mappings
        class_subjects_data = [
            (1, 1, 1), (1, 2, 1), (1, 3, 1), (1, 4, 1), (1, 9, 1), (1, 10, 1),  # CSE-A
            (2, 1, 1), (2, 2, 1), (2, 3, 1), (2, 4, 1), (2, 9, 1), (2, 10, 1),  # CSE-B
            (3, 5, 1), (3, 6, 1), (3, 9, 1), (3, 10, 1),  # ECE-A
            (4, 5, 1), (4, 6, 1), (4, 9, 1), (4, 10, 1),  # ECE-B
            (5, 7, 1), (5, 8, 1), (5, 9, 1), (5, 10, 1),  # MECH-A
            (6, 1, 1), (6, 2, 1), (6, 3, 1), (6, 4, 1), (6, 9, 1), (6, 10, 1)   # IT-A
        ]

        cursor.executemany("""
            INSERT IGNORE INTO class_subjects (class_id, subject_id, is_active)
            VALUES (%s, %s, %s)
        """, class_subjects_data)
        print("✅ Class-Subject mappings inserted")

        # Sample students (with hashed passwords)
        hashed_password = 'pbkdf2:sha256:600000$gupZ7NnYV7tFpfQM$a93fa09b6f4da31bc1c6e8dac6d73dc124f4f9a9b0b4f57c5daae03f1c7cb735'
        students_data = [
            ('pragyan', hashed_password, 'pragyan1@srms.com', '202500017', 'B.Tech', '1st Year', 'Computer Science', 0),
            ('priyanka', hashed_password, 'priyanka@srms.com', '202200013', 'B.Tech', '2nd Year', 'Computer Science', 0),
            ('swatee', hashed_password, 'swatee3@srms.com', '202100035', 'B.Tech', '3rd Year', 'Electronics', 0),
            ('shubham', hashed_password, 'shubham4@srms.com', '202000012', 'B.Tech', '4th Year', 'Mechanical', 0),
            ('rahul', hashed_password, 'rahul5@srms.com', '202200019', 'B.Tech', '2nd Year', 'Information Technology', 0)
        ]

        cursor.executemany("""
            INSERT IGNORE INTO users (username, password, email, roll_number, course, year, department, is_admin)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, students_data)
        print("✅ Sample students inserted")

        # Sample marks
        marks_data = [
            (1, 1, 'Data Structures', 'Computer Science', 85),
            (1, 2, 'Database Management', 'Computer Science', 92),
            (1, 3, 'Web Development', 'Computer Science', 88),
            (1, 4, 'OOPS with Java', 'Computer Science', 90),
            (2, 1, 'Data Structures', 'Computer Science', 78),
            (2, 2, 'Database Management', 'Computer Science', 82),
            (2, 3, 'Web Development', 'Computer Science', 75),
            (2, 4, 'OOPS with Java', 'Computer Science', 80),
            (3, 5, 'Digital Logic Design', 'Electronics', 87),
            (3, 6, 'Signals and Systems', 'Electronics', 84),
            (4, 7, 'Thermodynamics', 'Mechanical', 79),
            (4, 8, 'Fluid Mechanics', 'Mechanical', 81),
            (5, 1, 'Data Structures', 'Information Technology', 95),
            (5, 2, 'Database Management', 'Information Technology', 93),
            (5, 3, 'Web Development', 'Information Technology', 91)
        ]

        cursor.executemany("""
            INSERT IGNORE INTO marks (users_id, subject_id, subject, department, marks)
            VALUES (%s, %s, %s, %s, %s)
        """, marks_data)
        print("✅ Sample marks inserted")

        connection.commit()
        print("✅ Database schema and sample data initialized successfully!")

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