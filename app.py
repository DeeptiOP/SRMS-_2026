from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config

# Load environment variables from .env file
load_dotenv()

# Create Flask app with config
app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'production')])

# Ensure session is properly configured for CSRF
app.config['SESSION_TYPE'] = app.config.get('SESSION_TYPE', 'filesystem')
app.config['SESSION_PERMANENT'] = app.config.get('SESSION_PERMANENT', False)
app.config['SESSION_USE_SIGNER'] = app.config.get('SESSION_USE_SIGNER', True)
app.config['PERMANENT_SESSION_LIFETIME'] = app.config.get('PERMANENT_SESSION_LIFETIME', 3600)
app.config['SESSION_FILE_DIR'] = app.config.get('SESSION_FILE_DIR', '/tmp/flask_sessions')

# Initialize extensions
csrf = CSRFProtect(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=app.config['RATELIMIT_STORAGE_URL']
)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))

# Create handlers
console_handler = logging.StreamHandler()
file_handler = RotatingFileHandler(app.config['LOG_FILE'], maxBytes=10485760, backupCount=5)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Database configuration with connection pooling
db_config = {
    'host': app.config['DB_HOST'],
    'user': app.config['DB_USER'],
    'password': app.config['DB_PASSWORD'],
    'database': app.config['DB_NAME'],
    'port': int(os.getenv('DB_PORT', 3306)),
    'pool_name': 'srms_pool',
    'pool_size': 5,
    'pool_reset_session': True
}

# Create connection pool
try:
    connection_pool = MySQLConnectionPool(**db_config)
    logger.info("Database connection pool created successfully")
except Error as e:
    logger.error(f"Database connection pool error: {e}")
    connection_pool = None

def get_db_connection():
    """Get database connection from pool with error handling"""
    try:
        if connection_pool:
            conn = connection_pool.get_connection()
            return conn
        else:
            logger.error("Connection pool not available")
            return None
    except Error as e:
        logger.error(f"Database connection error: {e}")
        return None

def get_cursor(conn):
    """Get cursor from connection"""
    try:
        cursor = conn.cursor(dictionary=True)
        return cursor
    except Error as e:
        logger.error(f"Cursor creation error: {e}")
        return None

# Test database connection on startup
try:
    test_conn = get_db_connection()
    if test_conn and test_conn.is_connected():
        logger.info("Database connection test successful")
        test_conn.close()
    else:
        logger.error("Failed to establish database connection")
except Exception as e:
    logger.error(f"Database initialization error: {e}")

# Decorator for login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'users_id' not in session:
            flash('Please log in first', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator for admin required
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Admin access required', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function# ROUTES

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def index():
    """Login page for students and admins"""
    msg = ''
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'student')
        
        # Validate input
        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('index'))
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error. Please try again.', 'danger')
            return redirect(url_for('index'))
        
        cursor = get_cursor(conn)
        if not cursor:
            flash('Database connection error. Please try again.', 'danger')
            conn.close()
            return redirect(url_for('index'))
        
        try:
            cursor.execute("SELECT id, username, password, email, course, year, department, is_admin FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()
            
            if user:
                # Check password using hashing
                if check_password_hash(user['password'], password):
                    session['username'] = user['username']
                    session['users_id'] = user['id']
                    session['is_admin'] = user.get('is_admin', 0)
                    
                    # Check if role matches user's actual role
                    if role == 'admin' and not user.get('is_admin', 0):
                        flash('You are not registered as admin.', 'warning')
                        session.clear()
                        return redirect(url_for('index'))
                    if role == 'student' and user.get('is_admin', 0):
                        flash('You are not registered as student.', 'warning')
                        session.clear()
                        return redirect(url_for('index'))
                    
                    # Redirect based on actual role
                    if user.get('is_admin', 0):
                        flash(f'Welcome Admin {username}!', 'success')
                        return redirect(url_for('admin'))
                    else:
                        flash(f'Welcome {username}!', 'success')
                        return redirect(url_for('dashboard'))
                else:
                    flash('Invalid password. Please try again.', 'danger')
            else:
                flash('Username not found. Please register or check your username.', 'danger')
        
        except Error as e:
            logger.error(f"Login error: {e}")
            flash('An error occurred. Please try again.', 'danger')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('index.html', msg=msg)

@app.route('/dashboard')
@login_required
def dashboard():
    """Student dashboard showing their results"""
    users_id = session.get('users_id')
    
    # Prevent admin from accessing student dashboard
    if session.get('is_admin'):
        return redirect(url_for('admin'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error. Please try again.', 'danger')
        return redirect(url_for('index'))
    
    cursor = get_cursor(conn)
    if not cursor:
        flash('Database connection error. Please try again.', 'danger')
        conn.close()
        return redirect(url_for('index'))
    
    try:
        # Fetch student info from users table
        cursor.execute("SELECT username, email, course, year, department FROM users WHERE id = %s", (users_id,))
        student = cursor.fetchone()
        
        if not student:
            flash('Student record not found. Please log in again.', 'warning')
            session.clear()
            return redirect(url_for('index'))
        
        # Fetch marks
        cursor.execute("SELECT id, subject, marks, created_at FROM marks WHERE users_id = %s ORDER BY created_at DESC", (users_id,))
        rows = cursor.fetchall()
        
        results = {}
        total_marks = 0
        num_subjects = 0
        
        for row in rows:
            results[row['subject']] = row['marks']
            total_marks += row['marks']
            num_subjects += 1
        
        percentage = round(total_marks / num_subjects, 2) if num_subjects > 0 else 0
        
        # Grade logic
        if percentage >= 90:
            grade = 'A+'
        elif percentage >= 75:
            grade = 'A'
        elif percentage >= 60:
            grade = 'B'
        elif percentage >= 45:
            grade = 'C'
        elif percentage >= 35:
            grade = 'D'
        else:
            grade = 'F'
        
        return render_template('dashboard.html',
                               username=student['username'],
                               email=student['email'],
                               course=student['course'],
                               year=student['year'],
                               department=student['department'],
                               results=results,
                               total_marks=total_marks,
                               num_subjects=num_subjects,
                               percentage=percentage,
                               grade=grade)
    
    except Error as e:
        logger.error(f"Dashboard error: {e}")
        flash('An error occurred while loading dashboard. Please try again.', 'danger')
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

@app.route('/register', methods=['GET', 'POST'])       
@limiter.limit("5 per minute")
def register():
    """Student registration page"""
    msg = ''
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        email = request.form.get('email', '').strip()
        roll_number = request.form.get('roll_number', '').strip()
        course = request.form.get('course', '').strip()
        year = request.form.get('year', '').strip()
        department = request.form.get('department', '').strip()
        
        # Validation
        if not all([username, password, email, roll_number, course, year, department]):
            msg = 'All fields are required!'
            return render_template('register.html', msg=msg)
        
        if password != confirm_password:
            msg = 'Passwords do not match!'
            return render_template('register.html', msg=msg)
        
        if len(password) < 6:
            msg = 'Password must be at least 6 characters long!'
            return render_template('register.html', msg=msg)
        
        if '@' not in email:
            msg = 'Please enter a valid email!'
            return render_template('register.html', msg=msg)
        
        conn = get_db_connection()
        if not conn:
            msg = 'Database connection error. Please try again.'
            return render_template('register.html', msg=msg)
        
        cursor = get_cursor(conn)
        if not cursor:
            msg = 'Database connection error. Please try again.'
            conn.close()
            return render_template('register.html', msg=msg)
        
        try:
            # Check if username already exists
            cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
            if cursor.fetchone():
                msg = 'Username already exists! Please choose a different one.'
                return render_template('register.html', msg=msg)
            
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cursor.fetchone():
                msg = 'Email already registered! Please use a different email.'
                return render_template('register.html', msg=msg)
            
            # Check if roll number already exists
            cursor.execute("SELECT id FROM users WHERE roll_number=%s", (roll_number,))
            if cursor.fetchone():
                msg = 'Roll number already exists! Please use a different roll number.'
                return render_template('register.html', msg=msg)
            
            # Hash password
            hashed_password = generate_password_hash(password)
            
            # Insert new user
            cursor.execute(
                "INSERT INTO users (username, password, email, roll_number, course, year, department, is_admin) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (username, hashed_password, email, roll_number, course, year, department, 0)
            )
            conn.commit()
            msg = 'Registered successfully! Please log in.'
            return render_template('register.html', msg=msg)
        
        except Error as e:
            logger.error(f"Registration error: {e}")
            msg = 'An error occurred during registration. Please try again.'
            return render_template('register.html', msg=msg)
        finally:
            cursor.close()
            conn.close()
    
    return render_template('register.html')

@app.route('/admin')
@admin_required
def admin():
    """Admin dashboard - view all students"""
    search = request.args.get('search', '').strip()
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error. Please try again.', 'danger')
        return redirect(url_for('index'))
    
    cursor = get_cursor(conn)
    if not cursor:
        flash('Database connection error. Please try again.', 'danger')
        conn.close()
        return redirect(url_for('index'))
    
    try:
        if search:
            query = """
                SELECT id, username, department, course, year, email, roll_number
                FROM users
                WHERE is_admin = 0 AND (
                    username LIKE %s OR
                    email LIKE %s OR
                    department LIKE %s OR
                    course LIKE %s OR
                    roll_number LIKE %s
                )
                ORDER BY username ASC
            """
            like_search = f"%{search}%"
            cursor.execute(query, (like_search, like_search, like_search, like_search, like_search))
        else:
            cursor.execute("SELECT id, username, department, course, year, email, roll_number FROM users WHERE is_admin = 0 ORDER BY username ASC")
        
        students = cursor.fetchall()
        
        return render_template('admin.html', students=students, search=search)
    
    except Error as e:
        logger.error(f"Admin page error: {e}")
        flash('An error occurred while fetching students. Please try again.', 'danger')
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

@app.route('/marks', methods=['GET', 'POST'])
@admin_required
def marks():
    """Add, update, and view marks for students"""
    msg = ''
    username = request.args.get('username', '').strip()
    department = ''
    year = ''
    users_id = None
    student_marks = []
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error. Please try again.', 'danger')
        return redirect(url_for('admin'))
    
    cursor = get_cursor(conn)
    if not cursor:
        flash('Database connection error. Please try again.', 'danger')
        conn.close()
        return redirect(url_for('admin'))
    
    try:
        if username:
            cursor.execute("SELECT id, department, year FROM users WHERE username=%s AND is_admin=0", (username,))
            user_info = cursor.fetchone()
            if user_info:
                department = user_info['department']
                year = str(user_info['year'])
                users_id = user_info['id']
                
                # Fetch existing marks for this student
                cursor.execute(
                    "SELECT id, subject, marks, created_at FROM marks WHERE users_id=%s ORDER BY created_at DESC",
                    (users_id,)
                )
                student_marks = cursor.fetchall()
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            subject = request.form.get('subject', '').strip()
            department = request.form.get('department', '').strip()
            marks_value = request.form.get('marks', '').strip()
            
            # Validation
            if not all([username, subject, marks_value]):
                msg = 'All fields are required!'
            else:
                try:
                    marks_int = int(marks_value)
                    if marks_int < 0 or marks_int > 100:
                        msg = 'Marks must be between 0 and 100!'
                    else:
                        cursor.execute("SELECT id FROM users WHERE username=%s AND is_admin=0", (username,))
                        user = cursor.fetchone()
                        
                        if user:
                            # Check if marks already exist for this subject
                            cursor.execute(
                                "SELECT id FROM marks WHERE users_id=%s AND subject=%s",
                                (user['id'], subject)
                            )
                            existing = cursor.fetchone()
                            
                            if existing:
                                # Update existing marks
                                cursor.execute(
                                    "UPDATE marks SET marks=%s WHERE users_id=%s AND subject=%s",
                                    (marks_int, user['id'], subject)
                                )
                                msg = f"Marks updated successfully for {subject}!"
                            else:
                                # Insert new marks
                                cursor.execute(
                                    "INSERT INTO marks (users_id, subject, department, marks) VALUES (%s, %s, %s, %s)",
                                    (user['id'], subject, department, marks_int)
                                )
                                msg = f"Marks added successfully for {subject}!"
                            
                            conn.commit()
                            
                            # Refresh student_marks
                            cursor.execute(
                                "SELECT id, subject, marks, created_at FROM marks WHERE users_id=%s ORDER BY created_at DESC",
                                (user['id'],)
                            )
                            student_marks = cursor.fetchall()
                        else:
                            msg = 'Student not found.'
                except ValueError:
                    msg = 'Marks must be a valid number!'
    
    except Error as e:
        logger.error(f"Marks page error: {e}")
        msg = 'An error occurred. Please try again.'
    finally:
        cursor.close()
        conn.close()
    
    return render_template('marks.html', 
                           msg=msg, 
                           username=username, 
                           department=department, 
                           year=year,
                           student_marks=student_marks)

@app.route('/delete_mark/<int:mark_id>', methods=['POST'])
@admin_required
def delete_mark(mark_id):
    """Delete a specific mark entry"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = get_cursor(conn)
    if not cursor:
        conn.close()
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    try:
        cursor.execute("DELETE FROM marks WHERE id=%s", (mark_id,))
        conn.commit()
        return jsonify({'success': True, 'message': 'Mark deleted successfully'})
    except Error as e:
        logger.error(f"Delete mark error: {e}")
        return jsonify({'success': False, 'message': 'Error deleting mark'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin_register', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def admin_register():
    """Admin registration page"""
    msg = ''
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        email = request.form.get('email', '').strip()
        admin_key = request.form.get('admin_key', '').strip()
        
        # Validation
        if not all([username, password, email]):
            msg = 'All fields are required!'
            return render_template('admin_register.html', msg=msg)
        
        # Check admin registration key
        if admin_key != app.config['ADMIN_REGISTRATION_KEY']:
            msg = 'Invalid admin registration key!'
            msg = 'Invalid admin registration key!'
            return render_template('admin_register.html', msg=msg)
        
        if password != confirm_password:
            msg = 'Passwords do not match!'
            return render_template('admin_register.html', msg=msg)
        
        if len(password) < 6:
            msg = 'Password must be at least 6 characters long!'
            return render_template('admin_register.html', msg=msg)
        
        if '@' not in email:
            msg = 'Please enter a valid email!'
            return render_template('admin_register.html', msg=msg)
        
        conn = get_db_connection()
        if not conn:
            msg = 'Database connection error. Please try again.'
            return render_template('admin_register.html', msg=msg)
        
        cursor = get_cursor(conn)
        if not cursor:
            msg = 'Database connection error. Please try again.'
            conn.close()
            return render_template('admin_register.html', msg=msg)
        
        try:
            # Check if username already exists
            cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
            if cursor.fetchone():
                msg = 'Username already exists! Please choose a different one.'
                return render_template('admin_register.html', msg=msg)
            
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cursor.fetchone():
                msg = 'Email already registered! Please use a different email.'
                return render_template('admin_register.html', msg=msg)
            
            # Hash password
            hashed_password = generate_password_hash(password)
            
            # Insert new admin
            cursor.execute(
                "INSERT INTO users (username, password, email, course, year, department, is_admin) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                ('', hashed_password, email, '', '', '', 1)
            )
            # Update username after insert
            cursor.execute("UPDATE users SET username=%s WHERE email=%s", (username, email))
            conn.commit()
            
            msg = 'Admin registered successfully! Please log in.'
            return render_template('admin_register.html', msg=msg)
        
        except Error as e:
            logger.error(f"Admin registration error: {e}")
            msg = 'An error occurred during registration. Please try again.'
            return render_template('admin_register.html', msg=msg)
        finally:
            cursor.close()
            conn.close()
    
    return render_template('admin_register.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """View and edit user profile"""
    users_id = session.get('users_id')
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error. Please try again.', 'danger')
        return redirect(url_for('index'))
    
    cursor = get_cursor(conn)
    if not cursor:
        flash('Database connection error. Please try again.', 'danger')
        conn.close()
        return redirect(url_for('index'))
    
    try:
        cursor.execute("SELECT username, email, course, year, department FROM users WHERE id=%s", (users_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('index'))
        
        return render_template('profile.html', user=user)
    
    except Error as e:
        logger.error(f"Profile page error: {e}")
        flash('An error occurred while loading profile. Please try again.', 'danger')
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

@app.route('/classes', methods=['GET', 'POST'])
@admin_required
def classes():
    """Manage classes"""
    msg = ''
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin'))
    
    cursor = get_cursor(conn)
    if not cursor:
        flash('Database connection error', 'danger')
        conn.close()
        return redirect(url_for('admin'))
    
    try:
        if request.method == 'POST':
            class_name = request.form.get('class_name', '').strip()
            description = request.form.get('description', '').strip()
            year = request.form.get('year', '').strip()
            department = request.form.get('department', '').strip()
            
            if not class_name:
                msg = 'Class name is required!'
            else:
                try:
                    cursor.execute(
                        "INSERT INTO classes (class_name, description, year, department) VALUES (%s, %s, %s, %s)",
                        (class_name, description, year, department)
                    )
                    conn.commit()
                    msg = f'Class "{class_name}" added successfully!'
                except Error as e:
                    msg = 'Class name already exists!'
                    logger.error(f"Class insert error: {e}")
        
        # Fetch all classes
        cursor.execute("SELECT id, class_name, description, year, department FROM classes ORDER BY class_name ASC")
        all_classes = cursor.fetchall()
        
        return render_template('classes.html', classes=all_classes, msg=msg)
    
    except Error as e:
        logger.error(f"Classes page error: {e}")
        msg = 'An error occurred'
        return render_template('classes.html', classes=[], msg=msg)
    finally:
        cursor.close()
        conn.close()

@app.route('/classes/<int:class_id>', methods=['POST'])
@admin_required
def delete_class(class_id):
    """Delete a class"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = get_cursor(conn)
    if not cursor:
        conn.close()
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    try:
        cursor.execute("DELETE FROM classes WHERE id=%s", (class_id,))
        conn.commit()
        return jsonify({'success': True, 'message': 'Class deleted successfully'})
    except Error as e:
        logger.error(f"Delete class error: {e}")
        return jsonify({'success': False, 'message': 'Error deleting class'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/subjects', methods=['GET', 'POST'])
@admin_required
def subjects():
    """Manage subjects"""
    msg = ''
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin'))
    
    cursor = get_cursor(conn)
    if not cursor:
        flash('Database connection error', 'danger')
        conn.close()
        return redirect(url_for('admin'))
    
    try:
        if request.method == 'POST':
            subject_name = request.form.get('subject_name', '').strip()
            subject_code = request.form.get('subject_code', '').strip()
            description = request.form.get('description', '').strip()
            
            if not subject_name:
                msg = 'Subject name is required!'
            else:
                try:
                    cursor.execute(
                        "INSERT INTO subjects (subject_name, subject_code, description) VALUES (%s, %s, %s)",
                        (subject_name, subject_code, description)
                    )
                    conn.commit()
                    msg = f'Subject "{subject_name}" added successfully!'
                except Error as e:
                    msg = 'Subject already exists!'
                    logger.error(f"Subject insert error: {e}")
        
        # Fetch all subjects
        cursor.execute("SELECT id, subject_name, subject_code, description FROM subjects ORDER BY subject_name ASC")
        all_subjects = cursor.fetchall()
        
        return render_template('subjects.html', subjects=all_subjects, msg=msg)
    
    except Error as e:
        logger.error(f"Subjects page error: {e}")
        msg = 'An error occurred'
        return render_template('subjects.html', subjects=[], msg=msg)
    finally:
        cursor.close()
        conn.close()

@app.route('/subjects/<int:subject_id>', methods=['POST'])
@admin_required
def delete_subject(subject_id):
    """Delete a subject"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = get_cursor(conn)
    if not cursor:
        conn.close()
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    try:
        cursor.execute("DELETE FROM subjects WHERE id=%s", (subject_id,))
        conn.commit()
        return jsonify({'success': True, 'message': 'Subject deleted successfully'})
    except Error as e:
        logger.error(f"Delete subject error: {e}")
        return jsonify({'success': False, 'message': 'Error deleting subject'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/class_subjects', methods=['GET', 'POST'])
@admin_required
def class_subjects():
    """Manage class-subject combinations"""
    msg = ''
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin'))
    
    cursor = get_cursor(conn)
    if not cursor:
        flash('Database connection error', 'danger')
        conn.close()
        return redirect(url_for('admin'))
    
    try:
        if request.method == 'POST':
            class_id = request.form.get('class_id', '').strip()
            subject_id = request.form.get('subject_id', '').strip()
            is_active = request.form.get('is_active', 0)
            
            if not class_id or not subject_id:
                msg = 'Both class and subject are required!'
            else:
                try:
                    cursor.execute(
                        "INSERT INTO class_subjects (class_id, subject_id, is_active) VALUES (%s, %s, %s)",
                        (class_id, subject_id, is_active)
                    )
                    conn.commit()
                    msg = 'Class-Subject combination added successfully!'
                except Error as e:
                    msg = 'This combination already exists or invalid data!'
                    logger.error(f"Class-Subject insert error: {e}")
        
        # Fetch all classes
        cursor.execute("SELECT id, class_name FROM classes ORDER BY class_name ASC")
        all_classes = cursor.fetchall()
        
        # Fetch all subjects
        cursor.execute("SELECT id, subject_name FROM subjects ORDER BY subject_name ASC")
        all_subjects = cursor.fetchall()
        
        # Fetch all class-subject combinations
        cursor.execute("""
            SELECT cs.id, c.class_name, s.subject_name, cs.is_active 
            FROM class_subjects cs
            JOIN classes c ON cs.class_id = c.id
            JOIN subjects s ON cs.subject_id = s.id
            ORDER BY c.class_name, s.subject_name
        """)
        combinations = cursor.fetchall()
        
        return render_template('class_subjects.html', 
                               classes=all_classes, 
                               subjects=all_subjects, 
                               combinations=combinations, 
                               msg=msg)
    
    except Error as e:
        logger.error(f"Class-Subjects page error: {e}")
        msg = 'An error occurred'
        return render_template('class_subjects.html', 
                               classes=[], 
                               subjects=[], 
                               combinations=[], 
                               msg=msg)
    finally:
        cursor.close()
        conn.close()

@app.route('/class_subjects/<int:combination_id>/toggle', methods=['POST'])
@admin_required
def toggle_class_subject(combination_id):
    """Toggle active/inactive status for class-subject combination"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = get_cursor(conn)
    if not cursor:
        conn.close()
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    try:
        cursor.execute("SELECT is_active FROM class_subjects WHERE id=%s", (combination_id,))
        result = cursor.fetchone()
        if result:
            new_status = 1 - result['is_active']
            cursor.execute("UPDATE class_subjects SET is_active=%s WHERE id=%s", (new_status, combination_id))
            conn.commit()
            return jsonify({'success': True, 'message': 'Status toggled successfully', 'new_status': new_status})
        return jsonify({'success': False, 'message': 'Combination not found'}), 404
    except Error as e:
        logger.error(f"Toggle class-subject error: {e}")
        return jsonify({'success': False, 'message': 'Error toggling status'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/class_subjects/<int:combination_id>', methods=['POST'])
@admin_required
def delete_class_subject(combination_id):
    """Delete a class-subject combination"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = get_cursor(conn)
    if not cursor:
        conn.close()
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    try:
        cursor.execute("DELETE FROM class_subjects WHERE id=%s", (combination_id,))
        conn.commit()
        return jsonify({'success': True, 'message': 'Combination deleted successfully'})
    except Error as e:
        logger.error(f"Delete class-subject error: {e}")
        return jsonify({'success': False, 'message': 'Error deleting combination'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/notices', methods=['GET'])
def notices():
    """View all notices"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        if session.get('is_admin'):
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('dashboard'))
    
    cursor = get_cursor(conn)
    if not cursor:
        flash('Database connection error', 'danger')
        conn.close()
        if session.get('is_admin'):
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('dashboard'))
    
    try:
        cursor.execute("""
            SELECT n.id, n.title, n.content, u.username as admin_name, n.created_at 
            FROM notices n
            JOIN users u ON n.admin_id = u.id
            ORDER BY n.created_at DESC
        """)
        all_notices = cursor.fetchall()
        return render_template('notices.html', notices=all_notices)
    
    except Error as e:
        logger.error(f"Notices page error: {e}")
        flash('An error occurred while loading notices', 'danger')
        if session.get('is_admin'):
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('dashboard'))
    finally:
        cursor.close()
        conn.close()

@app.route('/add_notice', methods=['GET', 'POST'])
@admin_required
def add_notice():
    """Add a new notice"""
    msg = ''
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if not title or not content:
            msg = 'Title and content are required!'
        else:
            conn = get_db_connection()
            if not conn:
                msg = 'Database connection error'
            else:
                cursor = get_cursor(conn)
                if not cursor:
                    msg = 'Database connection error'
                    conn.close()
                else:
                    try:
                        cursor.execute(
                            "INSERT INTO notices (title, content, admin_id) VALUES (%s, %s, %s)",
                            (title, content, session.get('users_id'))
                        )
                        conn.commit()
                        msg = 'Notice added successfully!'
                        return render_template('add_notice.html', msg=msg)
                    except Error as e:
                        logger.error(f"Add notice error: {e}")
                        msg = 'An error occurred while adding notice'
                    finally:
                        cursor.close()
                        conn.close()
    
    return render_template('add_notice.html', msg=msg)

@app.route('/notices/<int:notice_id>', methods=['POST'])
@admin_required
def delete_notice(notice_id):
    """Delete a notice"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    cursor = get_cursor(conn)
    if not cursor:
        conn.close()
        return jsonify({'success': False, 'message': 'Database connection error'}), 500
    
    try:
        cursor.execute("DELETE FROM notices WHERE id=%s", (notice_id,))
        conn.commit()
        return jsonify({'success': True, 'message': 'Notice deleted successfully'})
    except Error as e:
        logger.error(f"Delete notice error: {e}")
        return jsonify({'success': False, 'message': 'Error deleting notice'}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
@admin_required
def edit_student(student_id):
    """Edit student information"""
    msg = ''
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('admin'))
    
    cursor = get_cursor(conn)
    if not cursor:
        flash('Database connection error', 'danger')
        conn.close()
        return redirect(url_for('admin'))
    
    try:
        if request.method == 'POST':
            roll_number = request.form.get('roll_number', '').strip()
            email = request.form.get('email', '').strip()
            course = request.form.get('course', '').strip()
            year = request.form.get('year', '').strip()
            department = request.form.get('department', '').strip()
            
            if not all([roll_number, email, course, year, department]):
                msg = 'All fields are required!'
            else:
                try:
                    cursor.execute(
                        "UPDATE users SET roll_number=%s, email=%s, course=%s, year=%s, department=%s WHERE id=%s",
                        (roll_number, email, course, year, department, student_id)
                    )
                    conn.commit()
                    msg = 'Student information updated successfully!'
                    flash('Student updated successfully!', 'success')
                    return redirect(url_for('admin'))
                except Error as e:
                    msg = 'Error updating student information'
                    logger.error(f"Edit student error: {e}")
        
        # Fetch student info
        cursor.execute("SELECT id, username, roll_number, email, course, year, department FROM users WHERE id=%s AND is_admin=0", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            flash('Student not found', 'danger')
            return redirect(url_for('admin'))
        
        return render_template('edit_student.html', student=student, msg=msg)
    
    except Error as e:
        logger.error(f"Edit student page error: {e}")
        flash('An error occurred', 'danger')
        return redirect(url_for('admin'))
    finally:
        cursor.close()
        conn.close()

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    msg = ''
    users_id = session.get('users_id')
    
    if request.method == 'POST':
        old_password = request.form.get('old_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not all([old_password, new_password, confirm_password]):
            msg = 'All fields are required!'
        elif len(new_password) < 6:
            msg = 'New password must be at least 6 characters!'
        elif new_password != confirm_password:
            msg = 'Passwords do not match!'
        else:
            conn = get_db_connection()
            if not conn:
                msg = 'Database connection error'
            else:
                cursor = get_cursor(conn)
                if not cursor:
                    msg = 'Database connection error'
                    conn.close()
                else:
                    try:
                        cursor.execute("SELECT password FROM users WHERE id=%s", (users_id,))
                        user = cursor.fetchone()
                        
                        if user and check_password_hash(user['password'], old_password):
                            hashed_password = generate_password_hash(new_password)
                            cursor.execute("UPDATE users SET password=%s WHERE id=%s", (hashed_password, users_id))
                            conn.commit()
                            msg = 'Password changed successfully!'
                            flash('Password changed successfully!', 'success')
                            return redirect(url_for('profile'))
                        else:
                            msg = 'Current password is incorrect!'
                    except Error as e:
                        logger.error(f"Change password error: {e}")
                        msg = 'An error occurred'
                    finally:
                        cursor.close()
                        conn.close()
    
    return render_template('change_password.html', msg=msg)

@app.route('/search_result', methods=['GET', 'POST'])
def search_result():
    """Student search result by roll number"""
    msg = ''
    results = {}
    student = None
    
    if request.method == 'POST':
        roll_number = request.form.get('roll_number', '').strip()
        
        if not roll_number:
            msg = 'Please enter a roll number!'
        else:
            conn = get_db_connection()
            if not conn:
                msg = 'Database connection error'
            else:
                cursor = get_cursor(conn)
                if not cursor:
                    msg = 'Database connection error'
                    conn.close()
                else:
                    try:
                        cursor.execute(
                            "SELECT id, username, roll_number, email, course, year, department FROM users WHERE roll_number=%s AND is_admin=0",
                            (roll_number,)
                        )
                        student = cursor.fetchone()
                        
                        if student:
                            cursor.execute(
                                "SELECT subject, marks FROM marks WHERE users_id=%s ORDER BY subject ASC",
                                (student['id'],)
                            )
                            marks_data = cursor.fetchall()
                            
                            total_marks = 0
                            num_subjects = 0
                            for row in marks_data:
                                results[row['subject']] = row['marks']
                                total_marks += row['marks']
                                num_subjects += 1
                            
                            if num_subjects == 0:
                                msg = 'No marks found for this student'
                        else:
                            msg = 'Student not found with this roll number!'
                    
                    except Error as e:
                        logger.error(f"Search result error: {e}")
                        msg = 'An error occurred'
                    finally:
                        cursor.close()
                        conn.close()
    
    return render_template('search_result.html', msg=msg, results=results, student=student)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {error}")
    return render_template('500.html'), 500
if __name__ == '__main__':
    print("=" * 50)
    print("STUDENT RESULT MANAGEMENT SYSTEM (SRMS)")
    print("=" * 50)
    print("Make sure your MySQL database is running with the schema from setup_database.sql")
    print(f"Server running on http://localhost:{os.getenv('PORT', 5000)}")
    print("=" * 50)
    app.run(
        debug=app.config['DEBUG'],
        port=int(os.getenv('PORT', 5000)),
        host=os.getenv('HOST', '127.0.0.1')
    )