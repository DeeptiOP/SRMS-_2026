-- SRMS Database Schema and Sample Data for Railway MySQL
-- Run this script in your Railway MySQL database

-- Create database (if needed)
CREATE DATABASE IF NOT EXISTS railway;
USE railway;

-- Users table
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Classes table
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Subjects table
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Class-Subjects junction table
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Marks table
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Notices table
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample data

-- Classes
INSERT IGNORE INTO classes (class_name, description, year, department) VALUES
('CSE-A', 'Computer Science Engineering - Section A', '2nd Year', 'Computer Science'),
('CSE-B', 'Computer Science Engineering - Section B', '2nd Year', 'Computer Science'),
('ECE-A', 'Electronics and Communication Engineering - Section A', '2nd Year', 'Electronics'),
('ECE-B', 'Electronics and Communication Engineering - Section B', '2nd Year', 'Electronics'),
('MECH-A', 'Mechanical Engineering - Section A', '2nd Year', 'Mechanical'),
('IT-A', 'Information Technology - Section A', '2nd Year', 'Information Technology');

-- Subjects
INSERT IGNORE INTO subjects (subject_name, subject_code, description, credits) VALUES
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

-- Class-Subject mappings
INSERT IGNORE INTO class_subjects (class_id, subject_id, is_active) VALUES
(1, 1, 1), (1, 2, 1), (1, 3, 1), (1, 4, 1), (1, 9, 1), (1, 10, 1),  -- CSE-A
(2, 1, 1), (2, 2, 1), (2, 3, 1), (2, 4, 1), (2, 9, 1), (2, 10, 1),  -- CSE-B
(3, 5, 1), (3, 6, 1), (3, 9, 1), (3, 10, 1),  -- ECE-A
(4, 5, 1), (4, 6, 1), (4, 9, 1), (4, 10, 1),  -- ECE-B
(5, 7, 1), (5, 8, 1), (5, 9, 1), (5, 10, 1),  -- MECH-A
(6, 1, 1), (6, 2, 1), (6, 3, 1), (6, 4, 1), (6, 9, 1), (6, 10, 1);  -- IT-A

-- Sample students (password is hashed for 'password123')
INSERT IGNORE INTO users (username, password, email, roll_number, course, year, department, is_admin) VALUES
('pragyan', 'pbkdf2:sha256:600000$gupZ7NnYV7tFpfQM$a93fa09b6f4da31bc1c6e8dac6d73dc124f4f9a9b0b4f57c5daae03f1c7cb735', 'pragyan1@srms.com', '202500017', 'B.Tech', '1st Year', 'Computer Science', 0),
('priyanka', 'pbkdf2:sha256:600000$gupZ7NnYV7tFpfQM$a93fa09b6f4da31bc1c6e8dac6d73dc124f4f9a9b0b4f57c5daae03f1c7cb735', 'priyanka@srms.com', '202200013', 'B.Tech', '2nd Year', 'Computer Science', 0),
('swatee', 'pbkdf2:sha256:600000$gupZ7NnYV7tFpfQM$a93fa09b6f4da31bc1c6e8dac6d73dc124f4f9a9b0b4f57c5daae03f1c7cb735', 'swatee3@srms.com', '202100035', 'B.Tech', '3rd Year', 'Electronics', 0),
('shubham', 'pbkdf2:sha256:600000$gupZ7NnYV7tFpfQM$a93fa09b6f4da31bc1c6e8dac6d73dc124f4f9a9b0b4f57c5daae03f1c7cb735', 'shubham4@srms.com', '202000012', 'B.Tech', '4th Year', 'Mechanical', 0),
('rahul', 'pbkdf2:sha256:600000$gupZ7NnYV7tFpfQM$a93fa09b6f4da31bc1c6e8dac6d73dc124f4f9a9b0b4f57c5daae03f1c7cb735', 'rahul5@srms.com', '202200019', 'B.Tech', '2nd Year', 'Information Technology', 0);

-- Admin user (username: admin, password: admin123)
INSERT IGNORE INTO users (username, password, email, roll_number, course, year, department, is_admin) VALUES
('admin', 'pbkdf2:sha256:600000$gupZ7NnYV7tFpfQM$a93fa09b6f4da31bc1c6e8dac6d73dc124f4f9a9b0b4f57c5daae03f1c7cb735', 'admin@srms.com', 'ADMIN001', 'Administration', 'N/A', 'Administration', 1);

-- Sample marks
INSERT IGNORE INTO marks (users_id, subject_id, subject, department, marks) VALUES
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
(5, 3, 'Web Development', 'Information Technology', 91);

-- Sample notice
INSERT IGNORE INTO notices (title, content, admin_id) VALUES
('Welcome to SRMS', 'Welcome to the Student Result Management System. This system helps manage student records, marks, and academic information efficiently.', 6);

-- Create analytical views for performance metrics
CREATE OR REPLACE VIEW student_performance AS
SELECT
    u.id,
    u.username,
    u.roll_number,
    u.department,
    COUNT(m.id) as total_subjects,
    ROUND(AVG(m.marks), 2) as average_marks,
    CASE
        WHEN AVG(m.marks) >= 90 THEN 'A+'
        WHEN AVG(m.marks) >= 80 THEN 'A'
        WHEN AVG(m.marks) >= 70 THEN 'B+'
        WHEN AVG(m.marks) >= 60 THEN 'B'
        WHEN AVG(m.marks) >= 50 THEN 'C'
        ELSE 'F'
    END as grade
FROM users u
LEFT JOIN marks m ON u.id = m.users_id
WHERE u.is_admin = 0
GROUP BY u.id, u.username, u.roll_number, u.department;

CREATE OR REPLACE VIEW department_stats AS
SELECT
    department,
    COUNT(DISTINCT u.id) as total_students,
    ROUND(AVG(m.marks), 2) as avg_department_marks,
    COUNT(m.id) as total_marks_entries
FROM users u
LEFT JOIN marks m ON u.id = m.users_id
WHERE u.is_admin = 0
GROUP BY department;

CREATE OR REPLACE VIEW subject_stats AS
SELECT
    s.subject_name,
    s.subject_code,
    COUNT(m.id) as students_enrolled,
    ROUND(AVG(m.marks), 2) as average_marks,
    MIN(m.marks) as lowest_marks,
    MAX(m.marks) as highest_marks
FROM subjects s
LEFT JOIN marks m ON s.id = m.subject_id
GROUP BY s.id, s.subject_name, s.subject_code;

COMMIT;