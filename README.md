# 📚 Student Result Management System (SRMS)

A comprehensive web-based application for managing student results, built with Flask and MySQL.

## 🎯 Features

✅ **User Authentication**
- Student Registration & Login
- Admin Registration & Login
- Password Hashing for Security
- Session Management

✅ **Student Dashboard**
- View Personal Profile
- View Academic Results
- View Grade & Percentage
- Download Results (Coming Soon)

✅ **Admin Features**
- View All Students
- Search Students by Username, Email, Department, Course
- Add/Edit/Delete Marks
- View Student Performance Analytics

✅ **Security Features**
- Password Hashing using Werkzeug
- Input Validation & Sanitization
- SQL Injection Prevention
- Session-based Authentication
- Admin Role-based Access Control
- Admin Registration Key Protection

✅ **User-Friendly Interface**
- Responsive Design
- Modern UI with Gradient Backgrounds
- Error Handling & Flash Messages
- Mobile Optimized

## 📋 System Requirements

- Python 3.7 or higher
- MySQL Server 5.7 or higher
- pip (Python Package Manager)

## 🚀 Production Deployment

For production deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### Quick Docker Deployment

```bash
# Setup environment
cp .env.example .env
# Edit .env with your secure values

# Deploy
docker-compose up -d

# Initialize admin
docker-compose exec srms python init_admin.py
```

## 🔒 Security Features

- Password hashing with Werkzeug
- CSRF protection with Flask-WTF
- Rate limiting with Flask-Limiter
- Input validation and sanitization
- SQL injection prevention
- Session-based authentication
- Admin role-based access control
- Secure admin registration with configurable key
```

The application will be available at: **http://localhost:5000**

## 👥 Default Credentials

### Admin Account (After Database Setup)
- **Username:** admin
- **Password:** admin123
- **Role:** Admin

### Default Admin Registration Key
```
ADMIN2024
```

⚠️ **IMPORTANT:** Change the admin registration key in `app.py` line for production:
```python
if admin_key != 'ADMIN2024':  # Change 'ADMIN2024' to your secure key
```

## 📱 How to Use

### For Students

1. **Register**
   - Go to http://localhost:5000
   - Click "Register here"
   - Fill in your details
   - Select your department and year
   - Create your account

2. **Login**
   - Select "Student" role
   - Enter your credentials
   - View your dashboard

3. **Dashboard**
   - View your profile information
   - See your marks by subject
   - Check your overall percentage
   - View your grade (A+, A, B, C, D, F)

### For Admins

1. **Register as Admin**
   - Click "Register as Admin" on login page
   - Enter admin registration key: **ADMIN2024**
   - Complete registration

2. **Login as Admin**
   - Select "Admin" role
   - Enter your credentials
   - Access admin dashboard

3. **Admin Dashboard**
   - View all registered students
   - Search students by name, email, department, or course
   - Add/Edit marks for each student
   - View and manage subject marks

## 📊 Grade Scale

| Percentage | Grade |
|-----------|-------|
| 90-100    | A+    |
| 75-89     | A     |
| 60-74     | B     |
| 45-59     | C     |
| 35-44     | D     |
| Below 35  | F     |

## 🗄️ Database Schema

### Users Table
- id (Primary Key)
- username (Unique)
- password (Hashed)
- email (Unique)
- course
- year
- department
- is_admin (0 = Student, 1 = Admin)
- created_at
- updated_at

### Marks Table
- id (Primary Key)
- users_id (Foreign Key)
- subject
- department
- marks (0-100)
- created_at
- updated_at

## 🔐 Security Notes

1. **Password Security**
   - All passwords are hashed using Werkzeug's generate_password_hash()
   - Passwords are never stored in plain text

2. **SQL Injection Prevention**
   - All database queries use parameterized statements
   - User input is properly sanitized

3. **Session Security**
   - Secure session management
   - Session validation on protected routes
   - Auto-logout available

4. **Admin Protection**
   - Admin registration requires a secure key
   - Admin-only routes are protected

## 🐛 Troubleshooting

### Database Connection Error
```
Error: Database connection error. Please try again.
```
**Solution:**
- Ensure MySQL server is running
- Check database credentials in app.py
- Verify database name is correct
- Run setup_database.sql if tables don't exist

### Import Error: mysql.connector
```
ModuleNotFoundError: No module named 'mysql.connector'
```
**Solution:**
```bash
pip install mysql-connector-python
```

### Port 5000 Already in Use
```
OSError: [Errno 10048] Only one usage of each socket address
```
**Solution:**
- Change port in app.py: `app.run(debug=True, port=5001)`
- Or kill the process using port 5000

## 📁 Project Structure

```
SRMS/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── setup_database.sql     # Database setup script
├── README.md             # Documentation
├── static/
│   ├── styles.css        # Login/Register styling
│   ├── dashboard.css     # Dashboard styling
│   ├── admin.css         # Admin panel styling
│   └── marks.css         # Marks management styling
└── templates/
    ├── index.html        # Login page
    ├── register.html     # Student registration
    ├── admin_register.html   # Admin registration
    ├── dashboard.html    # Student dashboard
    ├── admin.html        # Admin dashboard
    ├── marks.html        # Marks management
    ├── profile.html      # Student profile
    ├── 404.html          # 404 error page
    └── 500.html          # 500 error page
```

## 🚀 Future Enhancements

- [ ] Email Verification
- [ ] Reset Password Functionality
- [ ] Student Performance Analytics & Charts
- [ ] Bulk Mark Upload (CSV)
- [ ] Export Results to PDF
- [ ] Student Attendance Tracking
- [ ] CGPA Calculation
- [ ] Notification System
- [ ] Mobile App
- [ ] API Documentation

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the code comments in app.py
3. Verify database setup
4. Check browser console for JavaScript errors

## 📄 License

This project is provided as-is for educational purposes.

## 👨‍💻 Developer

Student Result Management System v2.0
Built with ❤️ using Flask & MySQL

---

**Happy Learning! 📚✨**
