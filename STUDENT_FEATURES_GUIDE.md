# 👨‍🎓 SRMS Student Features Guide

## Overview
This document provides a complete overview of all student functionalities in the Student Result Management System (SRMS).

---

## ✅ Implemented Student Features

### 1. **Search Results Using Roll ID**
**Route:** `/search_result`  
**Authentication:** Not required (Public access)  
**Methods:** GET, POST

**Features:**
- Search student results using Roll Number
- View student personal information:
  - Student Name (Username)
  - Roll Number
  - Email
  - Course
  - Year
  - Department
- View all marks/results for the student:
  - Subject Name
  - Marks obtained
- Responsive search interface
- Error handling for invalid or non-existent roll numbers

**Implementation Location:** [app.py](app.py#L1097-L1152)

**How to Use:**
1. Navigate to "Search Result" page (accessible from home page)
2. Enter the **Roll Number** to search
3. Click "Search" button
4. System displays:
   - **Student Information:** Name, Roll ID, Email, Course, Year, Department
   - **Marks Table:** All subjects and their marks
5. To search another student, clear the form and enter a different roll number

**Search Features:**
- Case-insensitive search
- Whitespace trimmed automatically
- Shows all subjects where marks are recorded
- Displays "No marks found" if student exists but has no marks

**Validation:**
- Roll number field cannot be empty
- Roll number must match a student in the system
- Displays appropriate error messages

**Template:** [templates/search_result.html](templates/search_result.html)

**Data Displayed:**
```
Student Information:
├── Student Name (Username)
├── Roll Number
├── Email
├── Course
├── Year
└── Department

Results Table:
├── Subject Name
└── Marks (0-100)
```

**Error Messages:**
- "Please enter a roll number!" - Empty search field
- "Student not found with this roll number!" - Roll number doesn't exist
- "No marks found for this student" - Student exists but no marks recorded
- "Database connection error" - Database unavailable

---

### 2. **View Notices**
**Route:** `/notices`  
**Authentication:** Not required (Public access for all users)  
**Methods:** GET

**Features:**
- View all system notices/announcements
- Display notice information:
  - Notice Title
  - Notice Content (full text)
  - Admin name who created the notice
  - Creation date and time
- Notices sorted by newest first (most recent on top)
- Admin action buttons (if logged in as admin):
  - Add new notice
  - Delete notices
- Clean, readable notice display format

**Implementation Location:** [app.py](app.py#L878-L916)

**How to Use:**
1. Click on "Notices" in the main menu/navigation
2. Browse all published notices
3. Read notice titles and full content
4. See which admin created each notice and when
5. Notices are organized by date (newest first)

**For Students:**
- View-only access to all notices
- Cannot add or delete notices
- Can read announcements about:
  - Exam schedules
  - Result declarations
  - Important dates
  - System maintenance

**For Admins:**
- Can add new notices (click "Add Notice" button)
- Can delete their own notices
- Can view all published notices

**Notices Display:**
```
Notice Card:
├── Title (Bold, prominent)
├── Content (Full text, can be multi-paragraph)
├── Created By: [Admin Name]
├── Created At: [Date & Time]
└── [Delete button - Admins only]
```

**Template:** [templates/notices.html](templates/notices.html)

---

## 🎓 Additional Student Features

### View Profile
**Route:** `/profile`  
**Authentication:** Login required  
**Methods:** GET

View your personal profile information:
- Username
- Email
- Course
- Year
- Department

**Template:** [templates/profile.html](templates/profile.html)

---

### Change Password
**Route:** `/change_password`  
**Authentication:** Login required  
**Methods:** GET, POST

Security feature to change your password:
- Verify current password
- Set new password (minimum 6 characters)
- Confirm new password match

**Features:**
- Old password verification (must be correct)
- New password validation (min 6 characters)
- Password confirmation match
- Secure hashing before storage
- Redirect to profile after success

**Template:** [templates/change_password.html](templates/change_password.html)

For detailed instructions, see [Admin Features Guide - Change Password](ADMIN_FEATURES_GUIDE.md#9-change-password)

---

### Student Dashboard
**Route:** `/dashboard`  
**Authentication:** Login required (Students only)  
**Methods:** GET

View personalized student dashboard:
- Your personal information
- Your results (if available)
- Grade and percentage
- Future: Download results feature

---

### Student Registration
**Route:** `/register`  
**Authentication:** Not required  
**Methods:** GET, POST

Register as a new student:
- Username (required, unique)
- Password (required, min 6 characters)
- Email (required, unique, valid format)
- Roll Number (optional)
- Department (optional)
- Course (optional)
- Year (optional)

**Template:** [templates/register.html](templates/register.html)

---

## 🔐 User Authentication

### Student Login
**Route:** `/index`  
**Methods:** GET, POST

Login with credentials:
1. Enter **Username**
2. Enter **Password**
3. Select Role: **Student** (from dropdown)
4. Click "Login"

Session-based authentication maintains login state during browsing.

---

## 📊 Database Tables Used

| Feature | Tables |
|---------|--------|
| Search Results | users, marks |
| View Notices | notices, users |
| View Profile | users |
| Change Password | users |
| Dashboard | users, marks |
| Student Registration | users |

---

## 🚀 Quick Access URLs for Students

| Feature | URL | Authentication |
|---------|-----|-----------------|
| Search Results | `/search_result` | Not required |
| View Notices | `/notices` | Not required |
| Student Dashboard | `/dashboard` | Login required |
| View Profile | `/profile` | Login required |
| Change Password | `/change_password` | Login required |
| Registration | `/register` | Not required |
| Login | `/index` | Not required |
| Logout | `/logout` | Login required |

---

## 📋 Search Results Workflow

**Step 1: Access Search Page**
- Navigate to `/search_result`
- See search form with Roll Number input

**Step 2: Enter Roll Number**
- Type your roll number or any student's roll number
- Example roll numbers: STU001, STU002, etc.

**Step 3: Search**
- Click "Search" button
- System queries database for matching student

**Step 4: View Results**
- If found: Display student info and all marks
- If not found: Show error message
- If no marks: Show student info with "No marks" message

**Step 5: Continue Searching**
- Enter another roll number to search again
- Page maintains search history in form

---

## 📣 View Notices Workflow

**Step 1: Access Notices Page**
- Click "Notices" in navigation menu
- Navigate to `/notices`

**Step 2: Browse Notices**
- See all notices in chronological order (newest first)
- Read notice titles
- Click on notice to expand and read full content

**Step 3: Identify Important Information**
- Check creator (which admin posted)
- Check date/time created
- Read full content for announcements

**Step 4: (Admin Only) Add Notice**
- Click "Add New Notice" button
- Enter title and content
- Click "Publish"

**Step 5: (Admin Only) Delete Notice**
- Click delete button on notice
- Confirm deletion
- Notice is removed immediately

---

## ✨ Key Features Summary

### Search Results
✅ Public access (no login required)
✅ Search by roll number
✅ Display student information
✅ Show all marks/results
✅ Error handling for invalid searches
✅ Responsive UI

### View Notices
✅ Public access (no login required)
✅ View all notices
✅ See admin creator name
✅ Display creation date/time
✅ Newest notices appear first
✅ Admin can add/delete notices
✅ Responsive UI

---

## 🔍 Example Searches

### Successful Search
```
Roll Number: STU001
Result:
  Student Name: john_doe
  Email: john@example.com
  Roll Number: STU001
  Course: B.Tech
  Year: 2
  Department: Computer Science
  
  Results:
  ├── Mathematics: 85
  ├── English: 78
  └── Science: 92
```

### No Marks Found
```
Roll Number: STU999
Result:
  Student Exists:
  ├── Name: new_student
  ├── Email: new@example.com
  └── No marks recorded yet
```

### Student Not Found
```
Roll Number: INVALID999
Result: "Student not found with this roll number!"
```

---

## 📝 Security & Privacy

### Public Features
- Search Results: Public but displays only basic academic info
- View Notices: Public announcements only

### Protected Features
- Dashboard: Login required
- Change Password: Login required
- View Profile: Login required

### Data Privacy
- Student marks visible only via roll number search
- Personal information shown only to student and admins
- Email addresses not publicly visible (except in student's own profile)

---

## 🎯 Common Tasks

### How to Check My Results
1. Go to `/search_result`
2. Enter your roll number
3. View your marks in the results table

### How to See Important Announcements
1. Click "Notices" in menu
2. Scroll through all announcements
3. Check dates for recent updates

### How to Download Results (Coming Soon)
- Feature under development
- Will be available in student dashboard
- Will generate PDF of results

### How to Check Exam Schedule
1. View Notices
2. Look for announcements from admin about schedules

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Student not found" | Check roll number spelling and format |
| "No marks found" | Results not yet published; contact admin |
| Can't see notices | Clear browser cache and reload |
| Search not working | Ensure roll number field is not empty |
| Database error | Contact administrator; server may be down |

---

## 📱 Responsive Design

- Mobile optimized layouts
- Touch-friendly buttons and forms
- Readable on all screen sizes
- Auto-adjusting tables for small screens

---

## ✅ Status Summary

**Student Features Implementation:**

✅ **Search Results by Roll ID** - Fully Implemented
- Database query functional
- Error handling complete
- UI responsive and user-friendly

✅ **View Notices** - Fully Implemented
- Display all notices
- Admin delete functionality
- Proper date formatting
- Public access enabled

✅ **Additional Features:**
- Student Dashboard: ✅ Complete
- View Profile: ✅ Complete
- Change Password: ✅ Complete
- Student Registration: ✅ Complete

---

**Project:** Student Result Management System (SRMS)  
**Framework:** Flask  
**Database:** MySQL  
**Last Updated:** 2024
