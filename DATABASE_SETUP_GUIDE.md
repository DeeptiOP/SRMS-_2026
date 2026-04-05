# 🗄️ SRMS Database Setup & Completion Guide

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Complete Setup Instructions](#complete-setup-instructions)
4. [Database Schema](#database-schema)
5. [Verification & Testing](#verification--testing)
6. [Troubleshooting](#troubleshooting)
7. [API Endpoints & Database Relationships](#api-endpoints--database-relationships)
8. [Data Dictionary](#data-dictionary)

---

## 🎯 Overview

This guide provides step-by-step instructions for completing the MySQL database setup for the Student Result Management System (SRMS). The database includes:

- ✅ 6 main tables with proper relationships
- ✅ 3 database views for analytics
- ✅ Sample data for testing
- ✅ Indexes for performance optimization
- ✅ Foreign key constraints for data integrity

---

## 📦 Prerequisites

Before starting, ensure you have:

- **MySQL Server** 5.7 or higher installed
- **Python** 3.7 or higher
- **Required Python Packages:**
  - Flask
  - mysql-connector-python
  - Werkzeug
  - python-dotenv

### Install Requirements

```bash
pip install -r requirements.txt
```

---

## 🚀 Complete Setup Instructions

### Step 1: Create the Database

Open MySQL command line or MySQL Workbench and run:

```bash
# Via command line
mysql -u root -p < setup_database.sql

# Or paste the entire setup_database.sql content into MySQL Workbench
```

**Or manually execute if the above doesn't work:**
1. Open MySQL Workbench
2. Create a new SQL script tab
3. Copy all content from `setup_database.sql`
4. Execute the script

### Step 2: Verify Database Creation

Run the verification script to ensure everything is set up correctly:

```bash
python verify_database.py
```

Expected output:
```
✅ Connected to database: srms_db
✅ Table 'users' exists
✅ Table 'classes' exists
✅ Table 'subjects' exists
✅ Table 'class_subjects' exists
✅ Table 'marks' exists
✅ Table 'notices' exists
✅ View 'student_overview' exists
✅ View 'class_performance' exists
✅ View 'subject_performance' exists
...
🎉 Database is properly configured!
```

### Step 3: Create Admin Account

Initialize the default admin user:

```bash
python init_admin.py
```

This will create:
- **Username:** admin
- **Password:** admin123
- **Email:** admin@srms.com
- **Role:** Administrator

### Step 4: Run the Application

Start the Flask development server:

```bash
python app.py
```

Expected output:
```
========================================
STUDENT RESULT MANAGEMENT SYSTEM (SRMS)
========================================
Make sure your MySQL database is running with the schema from setup_database.sql
Server running on http://localhost:5000
========================================
```

### Step 5: Access the Application

Open your browser and navigate to:

```
http://localhost:5000
```

**Login as Admin:**
- Username: `admin`
- Password: `admin123`
- Role: Select "Admin"

---

## 🏗️ Database Schema

### Table 1: Users

Stores both student and admin user accounts.

| Column | Type | Key | Description |
|--------|------|-----|-------------|
| id | INT | PRIMARY | Unique user identifier |
| username | VARCHAR(100) | UNIQUE | Login username |
| password | VARCHAR(255) | - | Hashed password |
| email | VARCHAR(100) | UNIQUE | User email address |
| roll_number | VARCHAR(50) | INDEX | Student roll number |
| course | VARCHAR(100) | - | Course name (e.g., B.Tech) |
| year | VARCHAR(50) | - | Academic year |
| department | VARCHAR(100) | INDEX | Department name |
| is_admin | INT | INDEX | 0=Student, 1=Admin |
| created_at | TIMESTAMP | - | Account creation time |
| updated_at | TIMESTAMP | - | Last update time |

### Table 2: Classes

Stores class information.

| Column | Type | Key | Description |
|--------|------|-----|-------------|
| id | INT | PRIMARY | Unique class identifier |
| class_name | VARCHAR(100) | UNIQUE | Class name (e.g., CSE-A) |
| description | TEXT | - | Class description |
| year | VARCHAR(50) | INDEX | Academic year |
| department | VARCHAR(100) | INDEX | Department name |
| created_at | TIMESTAMP | - | Creation time |
| updated_at | TIMESTAMP | - | Last update time |

### Table 3: Subjects

Stores subject/course information.

| Column | Type | Key | Description |
|--------|------|-----|-------------|
| id | INT | PRIMARY | Unique subject identifier |
| subject_name | VARCHAR(100) | UNIQUE | Subject name |
| subject_code | VARCHAR(50) | UNIQUE | Subject code (e.g., CS201) |
| description | TEXT | - | Subject description |
| credits | DECIMAL(3,1) | - | Credit hours |
| created_at | TIMESTAMP | - | Creation time |
| updated_at | TIMESTAMP | - | Last update time |

### Table 4: Class-Subjects (Junction Table)

Maps subjects to classes (many-to-many relationship).

| Column | Type | Key | Description |
|--------|------|-----|-------------|
| id | INT | PRIMARY | Unique mapping identifier |
| class_id | INT | FK | Reference to classes.id |
| subject_id | INT | FK | Reference to subjects.id |
| is_active | INT | - | 1=Active, 0=Inactive |
| created_at | TIMESTAMP | - | Creation time |
| updated_at | TIMESTAMP | - | Last update time |

### Table 5: Marks

Stores student marks/grades.

| Column | Type | Key | Description |
|--------|------|-----|-------------|
| id | INT | PRIMARY | Unique marks entry identifier |
| users_id | INT | FK | Reference to users.id |
| subject_id | INT | FK | Reference to subjects.id |
| subject | VARCHAR(100) | - | Subject name (for reference) |
| department | VARCHAR(100) | - | Department name |
| marks | INT | - | Marks obtained (0-100) |
| created_at | TIMESTAMP | - | Entry creation time |
| updated_at | TIMESTAMP | - | Last update time |

### Table 6: Notices

Stores announcements and notices.

| Column | Type | Key | Description |
|--------|------|-----|-------------|
| id | INT | PRIMARY | Unique notice identifier |
| title | VARCHAR(200) | - | Notice title |
| content | TEXT | - | Notice content |
| admin_id | INT | FK | Reference to users.id (admin) |
| created_at | TIMESTAMP | - | Creation time |
| updated_at | TIMESTAMP | - | Last update time |

---

## 📊 Database Views

### View 1: student_overview

Displays comprehensive student information with performance metrics.

**Query:**
```sql
SELECT 
    u.id, u.username, u.email, u.roll_number,
    u.course, u.year, u.department,
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
GROUP BY u.id
```

### View 2: class_performance

Shows performance metrics for each class.

**Query:**
```sql
SELECT 
    c.id, c.class_name, c.year, c.department,
    COUNT(DISTINCT u.id) as total_students,
    AVG(m.marks) as class_average,
    MAX(m.marks) as highest_mark,
    MIN(m.marks) as lowest_mark
FROM classes c
LEFT JOIN users u ON u.department = c.department
LEFT JOIN marks m ON u.id = m.users_id
WHERE u.is_admin = 0
GROUP BY c.id
```

### View 3: subject_performance

Shows performance metrics for each subject.

**Query:**
```sql
SELECT 
    s.id, s.subject_name, s.subject_code,
    COUNT(DISTINCT m.users_id) as students_enrolled,
    AVG(m.marks) as average_marks,
    MAX(m.marks) as highest_mark,
    MIN(m.marks) as lowest_mark,
    COUNT(CASE WHEN m.marks >= 40 THEN 1 END) as passed_count,
    COUNT(CASE WHEN m.marks < 40 THEN 1 END) as failed_count
FROM subjects s
LEFT JOIN marks m ON s.id = m.subject_id
GROUP BY s.id
```

---

## ✅ Verification & Testing

### Run the Verification Script

```bash
python verify_database.py
```

This checks:
- ✅ Database connection
- ✅ All tables exist
- ✅ All views exist
- ✅ Foreign key relationships
- ✅ Data integrity
- ✅ Indexes
- ✅ Sample data

### Test Database Queries

#### Query 1: View all students

```sql
SELECT username, email, department, course FROM users WHERE is_admin = 0;
```

#### Query 2: View student marks

```sql
SELECT u.username, m.subject, m.marks 
FROM users u 
JOIN marks m ON u.id = m.users_id 
WHERE u.username = 'student1';
```

#### Query 3: Check student overview

```sql
SELECT * FROM student_overview LIMIT 1;
```

#### Query 4: View class performance

```sql
SELECT * FROM class_performance;
```

#### Query 5: View subject performance

```sql
SELECT * FROM subject_performance;
```

---

## 🔧 Troubleshooting

### Issue 1: Database Connection Error

**Error:** `Database connection error. Please try again.`

**Solution:**
1. Verify MySQL is running
2. Check database configuration in `app.py`
3. Check `.env` file has correct credentials
4. Run `python verify_database.py`

### Issue 2: Table Not Found

**Error:** `Table 'srms_db.users' doesn't exist`

**Solution:**
1. Run `mysql -u root -p < setup_database.sql`
2. Verify your MySQL username and password
3. Check if the database `srms_db` exists:
   ```sql
   SHOW DATABASES;
   ```

### Issue 3: Foreign Key Constraint Fails

**Error:** `Cannot delete or update a parent row: a foreign key constraint fails`

**Solution:**
- Make sure you delete child records first
- Or disable foreign key checks temporarily:
  ```sql
  SET FOREIGN_KEY_CHECKS=0;
  -- Your DELETE/UPDATE statement
  SET FOREIGN_KEY_CHECKS=1;
  ```

### Issue 4: Admin Login Fails

**Error:** `Username not found` or `Invalid password`

**Solution:**
1. Re-run the admin initialization:
   ```bash
   python init_admin.py
   ```
2. Verify admin exists:
   ```sql
   SELECT username, email, is_admin FROM users WHERE is_admin = 1;
   ```

### Issue 5: Port Already in Use

**Error:** `Address already in use` when running `python app.py`

**Solution:**
1. Change the port in `app.py`:
   ```python
   app.run(debug=True, port=5001, host='127.0.0.1')  # Change 5000 to 5001
   ```
2. Or kill the process using port 5000:
   ```bash
   # Windows
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   
   # Linux/Mac
   lsof -i :5000
   kill -9 <PID>
   ```

---

## 🔗 API Endpoints & Database Relationships

### User Authentication Routes

| Route | Method | Database Access | Purpose |
|-------|--------|-----------------|---------|
| `/index` | GET, POST | users | User login |
| `/register` | GET, POST | users | Student registration |
| `/admin_register` | GET, POST | users | Admin registration |
| `/logout` | GET | - | Session cleanup |

### Student Routes

| Route | Method | Database Access | Purpose |
|-------|--------|-----------------|---------|
| `/dashboard` | GET | users, marks | View student results |
| `/profile` | GET | users | View student profile |
| `/change_password` | GET, POST | users | Change password |
| `/notices` | GET | notices, users | View announcements |
| `/search_result` | GET, POST | users, marks | Search by roll number |

### Admin Routes

| Route | Method | Database Access | Purpose |
|-------|--------|-----------------|---------|
| `/admin` | GET | users | View all students |
| `/marks` | GET, POST | users, marks | Add/edit marks |
| `/delete_mark/<id>` | POST | marks | Delete marks |
| `/classes` | GET, POST | classes | Manage classes |
| `/classes/<id>` | POST | classes | Delete class |
| `/subjects` | GET, POST | subjects | Manage subjects |
| `/subjects/<id>` | POST | subjects | Delete subject |
| `/class_subjects` | GET, POST | class_subjects, classes, subjects | Map subjects to classes |
| `/class_subjects/<id>/toggle` | POST | class_subjects | Toggle active status |
| `/class_subjects/<id>` | POST | class_subjects | Delete mapping |
| `/notices` | GET | notices, users | View notices |
| `/add_notice` | GET, POST | notices, users | Create notice |
| `/notices/<id>` | POST | notices | Delete notice |
| `/edit_student/<id>` | GET, POST | users | Edit student info |

---

## 📚 Data Dictionary

### Sample Data Included

#### Students (5 pre-configured)
- **user1:** student1@srms.com (CSE Department)
- **user2:** student2@srms.com (CSE Department)
- **user3:** student3@srms.com (ECE Department)
- **user4:** student4@srms.com (Mechanical Department)
- **user5:** student5@srms.com (IT Department)

#### Classes (6 pre-configured)
- CSE-A, CSE-B
- ECE-A, ECE-B
- MECH-A
- IT-A

#### Subjects (10 pre-configured)
- Data Structures (CS201)
- Database Management (CS202)
- Web Development (CS203)
- OOPS with Java (CS204)
- Digital Logic Design (EC201)
- Signals and Systems (EC202)
- Thermodynamics (ME201)
- Fluid Mechanics (ME202)
- Mathematics III (MA301)
- Physics II (PH301)

---

## 🔐 Security Considerations

### Password Hashing

All passwords are hashed using Werkzeug's `generate_password_hash()`:
- Algorithm: PBKDF2-SHA256
- Salt: Randomly generated
- Iterations: 600,000+

### SQL Injection Prevention

All queries use parameterized statements:
```python
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```

### Session Management

- Session data stored server-side
- Secure session key configured
- Auto-logout on session expiration

### Foreign Key Constraints

All relationships enforced at database level:
- `CASCADE` - Delete related records
- `SET NULL` - Clear reference on parent deletion

---

## 📈 Performance Optimization

### Indexes

- `idx_username` on users.username
- `idx_email` on users.email
- `idx_is_admin` on users.is_admin
- `idx_roll_number` on users.roll_number
- `idx_department` on users.department
- `idx_users_id` on marks.users_id
- `idx_subject` on marks.subject
- `idx_marks` on marks.marks

### Views

Pre-computed queries for:
- Student performance analysis
- Class performance metrics
- Subject difficulty analysis

---

## 🎓 Next Steps

1. ✅ Database setup complete
2. ✅ Admin account created
3. ✅ Sample data loaded
4. ⏭️ Customize sample data as needed
5. ⏭️ Add more students and marks
6. ⏭️ Configure email notifications (future enhancement)
7. ⏭️ Deploy to production server

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Run `python verify_database.py` for detailed diagnostics
3. Review database logs: `SHOW ENGINE INNODB STATUS;`
4. Check application logs in terminal output

---

**Last Updated:** April 2026  
**Version:** 2.0  
**Status:** Complete & Production Ready ✨
