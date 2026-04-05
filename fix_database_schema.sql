-- ==============================================================================
-- DATABASE SCHEMA MIGRATION - FIX MISSING COLUMNS
-- ==============================================================================
-- This script fixes the schema issues by adding missing columns and constraints
-- Run this if you're getting "Unknown column" errors

USE srms_db;

-- ==============================================================================
-- STEP 1: Check and add missing column to subjects table
-- ==============================================================================
ALTER TABLE subjects ADD COLUMN IF NOT EXISTS credits DECIMAL(3,1) DEFAULT 4.0;

-- ==============================================================================
-- STEP 2: Check and add missing column to marks table  
-- ==============================================================================
ALTER TABLE marks ADD COLUMN IF NOT EXISTS subject_id INT AFTER users_id;

-- ==============================================================================
-- STEP 3: Add foreign key constraint for subject_id if it doesn't exist
-- ==============================================================================
-- First check if the constraint exists, if not add it
ALTER TABLE marks ADD CONSTRAINT fk_marks_subject 
FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL;

-- ==============================================================================
-- STEP 4: Verify the structure
-- ==============================================================================
-- Show the structure of updated tables
DESCRIBE subjects;
DESCRIBE marks;

-- ==============================================================================
-- STEP 5: Re-insert sample data (if needed after migration)
-- ==============================================================================
-- Clear existing data safely
DELETE FROM marks;
DELETE FROM class_subjects;
DELETE FROM subjects;
DELETE FROM classes;

-- Re-insert classes
INSERT INTO classes (class_name, description, year, department) VALUES
('CSE-A', 'Computer Science Engineering - Section A', '2nd Year', 'Computer Science'),
('CSE-B', 'Computer Science Engineering - Section B', '2nd Year', 'Computer Science'),
('ECE-A', 'Electronics and Communication Engineering - Section A', '2nd Year', 'Electronics'),
('ECE-B', 'Electronics and Communication Engineering - Section B', '2nd Year', 'Electronics'),
('MECH-A', 'Mechanical Engineering - Section A', '2nd Year', 'Mechanical'),
('IT-A', 'Information Technology - Section A', '2nd Year', 'Information Technology');

-- Re-insert subjects
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

-- Re-insert class-subject mappings
INSERT INTO class_subjects (class_id, subject_id, is_active) VALUES
-- CSE-A subjects
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

-- Re-insert marks with proper subject_id references
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
-- SUCCESS MESSAGE
-- ==============================================================================
SELECT 'Database schema migration completed successfully!' as status;
