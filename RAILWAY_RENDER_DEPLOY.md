# Railway + Render Deployment Guide

## Your Railway Database Credentials
```
MYSQL_DATABASE: railway
MYSQL_PUBLIC_URL: mysql://root:ozLXsDoEIXYXsNJXJpxbcDXvTqkYzzSk@switchyard.proxy.rlwy.net:43529/railway
MYSQL_ROOT_PASSWORD: ozLXsDoEIXYXsNJXJpxbcDXvTqkYzzSk
MYSQL_URL: mysql://root:ozLXsDoEIXYXsNJXJpxbcDXvTqkYzzSk@mysql.railway.internal:3306/railway
MYSQLHOST: mysql.railway.internal
MYSQLDATABASE: railway
MYSQLPASSWORD: ozLXsDoEIXYXsNJXJpxbcDXvTqkYzzSk
MYSQLPORT: 3306
MYSQLUSER: root
```

## 🚀 Quick Deploy to Render

### Step 1: Connect Repository
1. Go to [Render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub account
4. Select repository: `DeeptiOP/SRMS-_2026`
5. Click "Connect"

### Step 2: Configure Service
```
Name: srms-app
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn --bind 0.0.0.0:$PORT wsgi:app
```

### Step 3: Set Environment Variables
In Render dashboard → Environment:

```
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-super-secret-key-here-make-it-very-long-and-random-123456789
WTF_CSRF_SECRET_KEY=csrf-secret-key-make-it-long-and-random-987654321
ADMIN_REGISTRATION_KEY=SECURE_ADMIN_KEY_FOR_PRODUCTION_2024

# Railway Database (Internal Connection - Recommended for Render)
DB_HOST=mysql.railway.internal
DB_USER=root
DB_PASSWORD=ozLXsDoEIXYXsNJXJpxbcDXvTqkYzzSk
DB_NAME=railway
DB_PORT=3306
```

### Step 4: Deploy
Click "Create Web Service" - Render will build and deploy automatically!

## 🔧 Local Development Setup

### Option 1: Use Railway Public URL (External)
Create `.env` file:
```env
DB_HOST=junction.proxy.rlwy.net
DB_USER=root
DB_PASSWORD=QJAklEaRgLuequxVOlMGRUKwZGCcMIwa
DB_NAME=railway
DB_PORT=37430
```

### Option 2: Use Railway CLI (Internal)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Run locally (will use internal connection)
python app.py
```

## 🗄️ Initialize Database

### Method 1: Railway CLI (Recommended)
```bash
railway run python setup_railway_db.py
```

### Method 2: Local with Public URL
```bash
# Set .env to use public URL
# DB_HOST=junction.proxy.rlwy.net
# DB_PORT=37430

python setup_railway_db.py
```

## 🔍 Testing Connection

### Test Database Connection
```python
from setup_railway_db import get_db_connection
conn = get_db_connection()
if conn:
    print("✅ Database connected successfully!")
    conn.close()
else:
    print("❌ Database connection failed")
```

### Test Full Application
```bash
python app.py
# Visit http://localhost:5000
```

## 🌐 Your Live Application
After deployment, your SRMS will be available at:
`https://your-render-service-name.onrender.com`

**Default Admin Login:**
- Username: `admin`
- Password: `admin123`
- ⚠️ **Change immediately!**

## 🔧 Troubleshooting

### Connection Issues
1. **From local machine**: Use public URL (`junction.proxy.rlwy.net:37430`)
2. **From Render**: Use internal URL (`mysql.railway.internal:3306`)
3. **Check credentials**: Verify all environment variables are set correctly

### Railway CLI Issues
```bash
# Re-link project
railway unlink
railway link

# Check variables
railway variables
```

### Render Deployment Issues
- Check build logs in Render dashboard
- Verify environment variables are set
- Ensure database is accessible from Render

## 📊 Monitoring
- **Render Dashboard**: View logs and metrics
- **Railway Dashboard**: Monitor database performance
- **Application Logs**: Check `app.log` for errors

Your SRMS is ready for production deployment! 🚀