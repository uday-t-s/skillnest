# SkillNest Installation & Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### 1. Navigate to Project Directory
```bash
cd c:\Users\benur\Desktop\skillnest_full_project_v4.css-update
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Migrations (Already Done!)
```bash
python manage.py migrate
```

### 5. Create Admin Account
```bash
python manage.py createsuperuser
```
Then fill in:
- **Username**: your_username
- **Email**: your_email@example.com
- **Password**: your_secure_password

### 6. Load Sample Data
```bash
Get-Content setup.py | python manage.py shell
```

### 7. Start Server
```bash
python manage.py runserver
```

✅ **Platform is live at**: http://localhost:8000

---

## 📋 What's Already Set Up

✓ Database configured (SQLite)
✓ All models created and migrated
✓ Sample data loaded (courses, jobs, skills, careers)
✓ Templates created
✓ URL routing configured
✓ Admin interface ready
✓ Test account ready (teacher1/teacher123)

---

## 🧪 Testing the Platform

### Test Login as Teacher (No Signup Needed!)
```
Username: teacher1
Password: teacher123
URL: http://localhost:8000/login
```

### Student Testing Flow
1. Go to http://localhost:8000
2. Click "Signup"
3. Choose "Student" role
4. Create account
5. Login and explore:
   - Browse courses: `/courses`
   - Enroll in courses
   - Complete lessons to earn skills
   - Get job recommendations: `/recommended-jobs`
   - Analyze skill gaps: `/skill-gap`

### Admin Panel Access
1. Login with your superuser account
2. Go to http://localhost:8000/admin
3. Manage everything: Users, Courses, Jobs, Skills, etc.

---

## 📁 Project Files Overview

| File | Purpose |
|------|---------|
| `manage.py` | Django management commands |
| `db.sqlite3` | Database (automatically created) |
| `requirements.txt` | Python dependencies |
| `setup.py` | Initial data setup |
| `skillnest/settings.py` | Project configuration |
| `skillnest_app/models.py` | Database models |
| `skillnest_app/views.py` | Application logic |
| `skillnest_app/recommendations.py` | Job recommendation engine |
| `skillnest_app/templates/` | HTML templates |
| `README.md` | Full documentation |

---

## 🎯 Key URLs

| URL | Description |
|-----|-------------|
| `/` | Home page |
| `/courses` | Browse courses |
| `/courses/<id>` | Course detail |
| `/jobs` | Job listings |
| `/portfolio/<username>` | Student portfolio |
| `/recommended-jobs` | AI job suggestions |
| `/skill-gap` | Skill gap analysis |
| `/admin` | Admin panel |
| `/login` | Login page |
| `/signup` | Registration |

---

## ⚙️ Configuration

### Change Database
Edit `skillnest/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'skillnest_db',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Change Port
```bash
python manage.py runserver 8080
```

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

---

## 🛠️ Useful Commands

```bash
# Make migrations (if you modify models)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Interactive shell
python manage.py shell

# Run tests
python manage.py test

# Check for issues
python manage.py check

# Clear cache
python manage.py clear_cache

# Create new app (if needed)
python manage.py startapp appname
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'django'"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### "Port 8000 already in use"
```bash
# Use different port
python manage.py runserver 8001
```

### "Database locked"
```bash
# Delete and recreate database
rm db.sqlite3
python manage.py migrate
```

### "Static files not loading"
```bash
# Collect static files
python manage.py collectstatic --noinput
```

### "Template not found"
```bash
# Ensure TEMPLATES setting is correct in settings.py
# Check that APP_DIRS = True
```

---

## 📊 Sample Data Included

### Skills (14 total)
- HTML, CSS, JavaScript, Python, Django, React
- SQL, MongoDB, Git, Docker, AWS
- Machine Learning, OOP, REST APIs

### Courses (6 total)
- HTML Basics
- CSS for Beginners
- JavaScript Essentials
- Python for Beginners
- Django Web Framework
- SQL Database Fundamentals

### Career Paths (4 total)
- Web Developer
- Python Developer
- Data Scientist
- DevOps Engineer

### Jobs (3 total)
- Junior Web Developer
- Python Backend Developer
- Full Stack Developer

### Test Account
- **Username**: teacher1
- **Password**: teacher123
- **Role**: Teacher

---

## 🚀 Production Deployment

### Before Going Live

1. **Update Settings**
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = 'generate-new-secret-key'
```

2. **Use Production Database**
```bash
# Install MySQL driver
pip install mysqlclient
```

3. **Collect Static Files**
```bash
python manage.py collectstatic --noinput
```

4. **Set Up Gunicorn**
```bash
pip install gunicorn
gunicorn skillnest.wsgi:application --bind 0.0.0.0:8000
```

5. **Use Nginx as Reverse Proxy**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
    
    location /static/ {
        alias /path/to/static/;
    }
}
```

### Deploy to Heroku

```bash
# Install Heroku CLI
# Then run:
heroku login
heroku create skillnest-app
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

---

## 📚 Learning Resources

- Django Official Docs: https://docs.djangoproject.com/
- Bootstrap Docs: https://getbootstrap.com/docs/
- Python Docs: https://docs.python.org/3/

---

## 💡 Tips & Tricks

### Enable Email Notifications (Gmail)
```python
# In settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Enable HTTPS Locally
```bash
pip install django-extensions
python manage.py runserver_plus --cert /tmp/cert
```

### Debug in Browser
Add to your views:
```python
from django.shortcuts import render
from django.http import JsonResponse

# Your view will show errors in browser
```

---

## ✅ Verification Checklist

- [ ] Project directory accessible
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Database migrated
- [ ] Sample data loaded
- [ ] Server starts without errors
- [ ] Admin panel accessible
- [ ] Test login works
- [ ] Sample courses visible
- [ ] All templates render

---

## 🎓 Next Steps

1. **Explore the Admin Panel**: `/admin`
2. **Try Signup**: Create a student account
3. **Enroll in Course**: Complete a full course
4. **Check Recommendations**: See job matches
5. **View Portfolio**: Share your achievements
6. **Customize**: Modify templates and styles

---

## 📞 Support & Help

If you encounter issues:

1. Check `Python` and `Django` versions
```bash
python --version
django-admin --version
```

2. Review Django logs
3. Check browser console (F12) for frontend errors
4. Run `python manage.py check` for project issues

---

## 🎉 You're All Set!

Your SkillNest platform is ready to use. Start by:

```bash
python manage.py runserver
```

Then visit: **http://localhost:8000** 🚀

Enjoy learning! 📚
