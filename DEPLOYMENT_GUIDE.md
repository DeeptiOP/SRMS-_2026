# 🚀 Production Deployment Guide for SRMS

## Prerequisites

- GitHub account
- Render account (https://render.com)
- Railway account (https://railway.app)
- Git installed locally

## Quick Deploy: Render + Railway (Recommended)

### Step 1: Push Code to GitHub

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit"

# Create GitHub repository and push
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

### Step 2: Setup Railway Database

1. Go to [Railway.app](https://railway.app) and create account
2. Click "New Project" → "Database" → "MySQL"
3. Wait for database to be provisioned
4. Go to "Variables" tab and copy the connection details:
   - `MYSQLHOST`
   - `MYSQLUSER`
   - `MYSQLPASSWORD`
   - `MYSQLDATABASE`
   - `MYSQLPORT`

### Step 3: Deploy to Render

1. Go to [Render.com](https://render.com) and create account
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: srms-app
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT wsgi:app`

### Step 4: Set Environment Variables in Render

In your Render service dashboard, go to "Environment" and add:

```
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
WTF_CSRF_SECRET_KEY=another-long-random-key-for-csrf
ADMIN_REGISTRATION_KEY=SECURE_ADMIN_KEY_FOR_PRODUCTION
DB_HOST=YOUR_RAILWAY_MYSQLHOST
DB_USER=YOUR_RAILWAY_MYSQLUSER
DB_PASSWORD=YOUR_RAILWAY_MYSQLPASSWORD
DB_NAME=YOUR_RAILWAY_MYSQLDATABASE
LOG_LEVEL=INFO
LOG_FILE=app.log
```

### Step 5: Initialize Database

After deployment, run the database setup:

```bash
# SSH into Railway database or use Railway CLI
railway run python setup_railway_db.py
```

Or manually run the SQL script in Railway's database console.

### Step 6: Access Your Application

Your SRMS application will be available at: `https://your-service-name.onrender.com`

**Default Admin Login:**
- Username: `admin`
- Password: `admin123`
- Change this immediately after first login!

## Option 1: Docker Deployment (Recommended)

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your secure values
nano .env
```

### 2. Database Setup

The docker-compose.yml includes MySQL setup. The database will be initialized automatically.

### 3. Deploy

```bash
# Build and start services
docker-compose up -d

# Check logs
docker-compose logs -f srms

# Create admin user
docker-compose exec srms python init_admin.py
```

### 4. Access

- Application: http://localhost:5000
- MySQL: localhost:3306

## Option 2: Manual Deployment

### 1. System Requirements

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip mysql-server nginx

# CentOS/RHEL
sudo yum install python3 python3-pip mysql-server nginx
```

### 2. Database Setup

```bash
# Start MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# Secure MySQL installation
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p
```

```sql
CREATE DATABASE srms_db;
CREATE USER 'srms_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON srms_db.* TO 'srms_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

```bash
# Import schema
mysql -u srms_user -p srms_db < setup_database.sql
```

### 3. Application Setup

```bash
# Clone/download project
cd /var/www
sudo mkdir srms
sudo chown $USER:$USER srms
cd srms

# Copy files and setup
cp .env.example .env
nano .env  # Configure your settings

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize admin
python init_admin.py
```

### 4. Gunicorn Setup

```bash
# Install gunicorn system-wide
sudo pip3 install gunicorn

# Create systemd service
sudo nano /etc/systemd/system/srms.service
```

Add this content:

```ini
[Unit]
Description=SRMS Flask Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/srms
Environment="PATH=/var/www/srms/venv/bin"
ExecStart=/var/www/srms/venv/bin/gunicorn --workers 3 --bind unix:srms.sock -m 007 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl start srms
sudo systemctl enable srms
```

### 5. Nginx Setup

```bash
sudo nano /etc/nginx/sites-available/srms
```

Add this content:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static {
        alias /var/www/srms/static;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/srms/srms.sock;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/srms /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## HTTPS Setup (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal is enabled by default
```

## Cloud Deployments

### Heroku

1. Create Heroku app
2. Add MySQL add-on (ClearDB or JawsDB)
3. Set environment variables
4. Deploy via git or Docker

### AWS

1. EC2 instance with Ubuntu
2. RDS MySQL instance
3. Follow manual deployment steps
4. Use ELB for load balancing

### DigitalOcean

1. Droplet with Ubuntu
2. Managed MySQL database
3. Follow manual deployment steps

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY and CSRF keys
- [ ] Enable HTTPS
- [ ] Configure firewall (ufw/iptables)
- [ ] Regular backups
- [ ] Monitor logs
- [ ] Keep dependencies updated

## Monitoring

```bash
# Check application status
sudo systemctl status srms

# View logs
sudo journalctl -u srms -f

# Check nginx status
sudo systemctl status nginx
```

## Backup Strategy

```bash
# Database backup
mysqldump -u srms_user -p srms_db > backup_$(date +%Y%m%d).sql

# Application backup
tar -czf srms_backup_$(date +%Y%m%d).tar.gz /var/www/srms
```

## Troubleshooting

### Common Issues

1. **Database connection failed**
   - Check MySQL is running
   - Verify credentials in .env
   - Check firewall settings

2. **Application not starting**
   - Check logs: `docker-compose logs` or `journalctl -u srms`
   - Verify Python dependencies
   - Check file permissions

3. **Static files not loading**
   - Verify nginx configuration
   - Check file permissions on static folder

### Performance Tuning

- Adjust gunicorn workers based on CPU cores
- Enable MySQL query caching
- Use Redis for session storage in production
- Implement CDN for static assets