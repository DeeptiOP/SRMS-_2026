-- ==============================================================================
-- STUDENT RESULT MANAGEMENT SYSTEM (SRMS) - Complete Database Setup Script
-- ==============================================================================
-- This script creates a fully configured MySQL database with all necessary tables,
-- relationships, indexes, sample data, and views for the SRMS application.
-- 
-- INSTRUCTIONS:
-- 1. Open MySQL Command Line or MySQL Workbench
-- 2. Run: mysql -u root -p < setup_database.sql
-- 3. Or manually copy-paste this entire script into MySQL client
-- 4. Run init_admin.py to create the first admin user
--
-- DEFAULT ADMIN LOGIN (after running init_admin.py):
-- Username: admin
-- Password: admin123
-- ==============================================================================

-- Create Database
CREATE DATABASE IF NOT EXISTS srms_db;
USE srms_db;

-- Enable foreign key constraints
SET FOREIGN_KEY_CHECKS=1;

-- ==============================================================================
-- TABLE 1: USERS TABLE (Students and Admins)
-- ==============================================================================
DROP TABLE IF EXISTS notices;
DROP TABLE IF EXISTS marks;
DROP TABLE IF EXISTS class_subjects;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS classes;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
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
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- TABLE 2: CLASSES TABLE
-- ==============================================================================
CREATE TABLE classes (
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
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- TABLE 3: SUBJECTS TABLE
-- ==============================================================================
CREATE TABLE subjects (
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
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- TABLE 4: CLASS-SUBJECTS JUNCTION TABLE
-- ==============================================================================
CREATE TABLE class_subjects (
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
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- TABLE 5: MARKS TABLE
-- ==============================================================================
CREATE TABLE marks (
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
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- TABLE 6: NOTICES TABLE
-- ==============================================================================
CREATE TABLE notices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    admin_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_admin_id (admin_id),
    INDEX idx_created_at (created_at)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- SAMPLE DATA - CLASSES
-- ==============================================================================
-- Note: Make sure to run init_admin.py to create the admin user first
INSERT INTO classes (class_name, description, year, department) VALUES
('CSE-A', 'Computer Science Engineering - Section A', '2nd Year', 'Computer Science'),
('CSE-B', 'Computer Science Engineering - Section B', '2nd Year', 'Computer Science'),
('ECE-A', 'Electronics and Communication Engineering - Section A', '2nd Year', 'Electronics'),
('ECE-B', 'Electronics and Communication Engineering - Section B', '2nd Year', 'Electronics'),
('MECH-A', 'Mechanical Engineering - Section A', '2nd Year', 'Mechanical'),
('IT-A', 'Information Technology - Section A', '2nd Year', 'Information Technology');

-- ==============================================================================
-- SAMPLE DATA - SUBJECTS
-- ==============================================================================
INSERT INTO subjects (subject_name, subject_code, description, credits) VALUES
('Data Structures', 'CS201', 'Study of data structures and algorithms', 4.0),
('Database Management', 'CS202', 'Relational database design and SQL', 4.0),
('Web Development', 'CS203', 'Frontend and backend web development', 4.0),
('OOPS with Java', 'CS204', 'Object-oriented programming concepts', 4.0),
('Digital Logic Design', 'EC201', 'Boolean algebra and logic circuits', 3.0),
('Signals and Systems', 'EC202', 'Analog and digital signal processing', 4.0),
('Thermodynamics', 'ME201', 'Laws of thermodynamics and applications', 4.0),
('Fluid Mechanics', 'ME202', 'Study of fluid flow characteristics', 4.0),
('Mathematics III', 'MA301', 'Calculus and Differential Equations', 4.0),
('Physics II', 'PH301', 'Electromagnetic theory and optics', 4.0);

-- ==============================================================================
-- SAMPLE DATA - CLASS-SUBJECT MAPPINGS
-- ==============================================================================
-- CSE-A subjects
INSERT INTO class_subjects (class_id, subject_id, is_active) VALUES
(1, 1, 1), (1, 2, 1), (1, 3, 1), (1, 4, 1), (1, 9, 1), (1, 10, 1),
-- CSE-B subjects
(2, 1, 1), (2, 2, 1), (2, 3, 1), (2, 4, 1), (2, 9, 1), (2, 10, 1),
-- ECE-A subjects
(3, 5, 1), (3, 6, 1), (3, 9, 1), (3, 10, 1),
-- ECE-B subjects
(4, 5, 1), (4, 6, 1), (4, 9, 1), (4, 10, 1),
-- MECH-A subjects
(5, 7, 1), (5, 8, 1), (5, 9, 1), (5, 10, 1),
-- IT-A subjects
(6, 1, 1), (6, 2, 1), (6, 3, 1), (6, 4, 1), (6, 9, 1), (6, 10, 1);

-- ==============================================================================
-- SAMPLE DATA - STUDENTS
-- ==============================================================================
-- Note: Passwords are hashed using werkzeug.security.generate_password_hash
-- For sample data, set actual passwords using init_admin.py after database creation

INSERT INTO users (username, password, email, roll_number, course, year, department, is_admin) VALUES
-- These are placeholder passwords. Run proper password generation for production
('pragyan', 'pbkdf2:sha256:600000$gupZ7NnYV7tFpfQM$a93fa09b6f4da31bc1c6e8dac6d73dc124f4f9a9b0b4f57c5daae03f1c7cb735', 'pragyan1@srms.com', '202500017', 'B.Tech', '1nd Year', 'Computer Science', 0),
('priyanka', 'pbkdf2:sha256:600000$gupZ7NnYV7tFpfQM$a93fa09b6f4da31bc1c6e8dac6d73dc124f4f9a9b0b4f57c5daae03f1c7cb735', 'priyanka@srms.com', '202200013', 'B.Tech', '2nd Year', 'Computer Science', 0),
('swatee', 'pbkdf2:sha256:600000$gupZ7NnYV7tFpfQM$a93fa09b6f4da31bc1c6e8dac6d73dc124f4f9a9b0b4f57c5daae03f1c7cb735', 'swatee3@srms.com', '202100035', 'B.Tech', '3nd Year', 'Electronics', 0),
('shubham', 'pbkdf2:sha256:600000$gupZ7NnYV7tFpfQM$a93fa09b6f4da31bc1c6e8dac6d73dc124f4f9a9b0b4f57c5daae03f1c7cb735', 'shubham4@srms.com', '202000012', 'B.Tech', '4nd Year', 'Mechanical', 0),
('rahul', 'pbkdf2:sha256:600000$gupZ7NnYV7tFpfQM$a93fa09b6f4da31bc1c6e8dac6d73dc124f4f9a9b0b4f57c5daae03f1c7cb735', 'rahul5@srms.com', '202200019', 'B.Tech', '2nd Year', 'Information Technology', 0);

-- ==============================================================================
-- SAMPLE DATA - MARKS
-- ==============================================================================
-- Get the student IDs first (Assuming students default to IDs 1-5)
INSERT INTO marks (users_id, subject_id, subject, department, marks) VALUES
-- Student 1 (CSE)
(1, 1, 'Data Structures', 'Computer Science', 85),
(1, 2, 'Database Management', 'Computer Science', 92),
(1, 3, 'Web Development', 'Computer Science', 88),
(1, 4, 'OOPS with Java', 'Computer Science', 90),
-- Student 2 (CSE)
(2, 1, 'Data Structures', 'Computer Science', 78),
(2, 2, 'Database Management', 'Computer Science', 82),
(2, 3, 'Web Development', 'Computer Science', 75),
(2, 4, 'OOPS with Java', 'Computer Science', 80),
-- Student 3 (ECE)
(3, 5, 'Digital Logic Design', 'Electronics', 87),
(3, 6, 'Signals and Systems', 'Electronics', 84),
-- Student 4 (Mechanical)
(4, 7, 'Thermodynamics', 'Mechanical', 79),
(4, 8, 'Fluid Mechanics', 'Mechanical', 81),
-- Student 5 (IT)
(5, 1, 'Data Structures', 'Information Technology', 95),
(5, 2, 'Database Management', 'Information Technology', 93),
(5, 3, 'Web Development', 'Information Technology', 91);

-- ==============================================================================
-- SAMPLE DATA - NOTICES
-- ==============================================================================
-- Note: Replace admin_id with actual admin user ID after creating admin account
-- This will be populated after running init_admin.py

-- ==============================================================================
-- CREATE VIEWS
-- ==============================================================================

-- Student Overview View
CREATE OR REPLACE VIEW student_overview AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.roll_number,
    u.course,
    u.year,
    u.department,
    COUNT(m.id) as total_subjects,
    AVG(m.marks) as average_marks,
    MAX(m.marks) as highest_mark,
    MIN(m.marks) as lowest_mark,
    CASE 
        WHEN AVG(m.marks) >= 90 THEN 'A+'
        WHEN AVG(m.marks) >= 75 THEN 'A'
        WHEN AVG(m.marks) >= 60 THEN 'B'
        WHEN AVG(m.marks) >= 45 THEN 'C'
        WHEN AVG(m.marks) >= 35 THEN 'D'
        ELSE 'F'
    END as grade
FROM users u
LEFT JOIN marks m ON u.id = m.users_id
WHERE u.is_admin = 0
GROUP BY u.id, u.username, u.email, u.roll_number, u.course, u.year, u.department;

-- Class Performance View
CREATE OR REPLACE VIEW class_performance AS
SELECT 
    c.id,
    c.class_name,
    c.year,
    c.department,
    COUNT(DISTINCT u.id) as total_students,
    AVG(m.marks) as class_average,
    MAX(m.marks) as highest_mark,
    MIN(m.marks) as lowest_mark
FROM classes c
LEFT JOIN users u ON u.department = c.department
LEFT JOIN marks m ON u.id = m.users_id
WHERE u.is_admin = 0
GROUP BY c.id, c.class_name, c.year, c.department;

-- Subject Performance View
CREATE OR REPLACE VIEW subject_performance AS
SELECT 
    s.id,
    s.subject_name,
    s.subject_code,
    COUNT(DISTINCT m.users_id) as students_enrolled,
    AVG(m.marks) as average_marks,
    MAX(m.marks) as highest_mark,
    MIN(m.marks) as lowest_mark,
    COUNT(CASE WHEN m.marks >= 40 THEN 1 END) as passed_count,
    COUNT(CASE WHEN m.marks < 40 THEN 1 END) as failed_count
FROM subjects s
LEFT JOIN marks m ON s.id = m.subject_id
GROUP BY s.id, s.subject_name, s.subject_code;

-- ==============================================================================
-- INDEXES FOR OPTIMIZATION
-- ==============================================================================
-- Additional indexes for frequently used queries
ALTER TABLE marks ADD INDEX idx_created_at (created_at);
ALTER TABLE notices ADD INDEX idx_updated_at (updated_at);
ALTER TABLE users ADD INDEX idx_created_at (created_at);

-- ==============================================================================
-- DATABASE STATISTICS AND VERIFICATION
-- ==============================================================================
SELECT '========================================' as Status;
SELECT '✅ SRMS Database Setup Complete!' as Status;
SELECT '========================================' as Status;
SELECT '' as '';
SELECT 'Tables Created:' as '';
SELECT '- users' as '';
SELECT '- classes' as '';
SELECT '- subjects' as '';
SELECT '- class_subjects' as '';
SELECT '- marks' as '';
SELECT '- notices' as '';
SELECT '' as '';
SELECT 'Views Created:' as '';
SELECT '- student_overview' as '';
SELECT '- class_performance' as '';
SELECT '- subject_performance' as '';
SELECT '' as '';
SELECT 'Sample Data Inserted:' as '';
SELECT CONCAT('Users: ', (SELECT COUNT(*) FROM users)) as '';
SELECT CONCAT('Classes: ', (SELECT COUNT(*) FROM classes)) as '';
SELECT CONCAT('Subjects: ', (SELECT COUNT(*) FROM subjects)) as '';
SELECT CONCAT('Marks: ', (SELECT COUNT(*) FROM marks)) as '';
SELECT '' as '';
SELECT 'NEXT STEP:' as '';
SELECT '1. Run: python init_admin.py' as '';
SELECT '2. Use credentials to log in as admin' as '';
SELECT '3. Start using the system!' as '';
SELECT '========================================' as Status;
