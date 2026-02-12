# SkillNest - Free Education & Placement Platform

A comprehensive Django-based web application that provides free tech courses, tracks student progress, issues certificates, and recommends jobs based on learned skills.

## Features

### 👨‍🎓 For Students
- **Browse & Enroll in Courses**: Explore 100% free courses across various tech categories
- **Track Progress**: Monitor your learning journey with visual progress bars
- **Earn Certificates**: Get recognized certificates upon course completion
- **Build Portfolio**: Create a public portfolio showcasing your skills and achievements
- **AI Job Recommendations**: Get intelligent job suggestions based on your learned skills
- **Skill Gap Analysis**: Identify missing skills for your target career path

### 👨‍🏫 For Teachers
- **Create Courses**: Develop and manage your own courses
- **Track Enrollments**: Monitor student progress and engagement
- **Add Lessons**: Structure courses with multiple lessons
- **Post Jobs**: Create job opportunities for students

### 👨‍💼 For Admin/HR
- **Manage Platform**: Control all users, courses, skills, and jobs
- **Analytics Dashboard**: View platform statistics and engagement
- **Job Management**: Post and manage job listings
- **User Management**: Handle user roles and permissions

## Tech Stack

- **Backend**: Django 5.2 (Python 3.10+)
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Database**: SQLite (Development) / MySQL (Production-ready)
- **Job Recommendation**: Simple rule-based algorithm (Python)

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git (optional)

### Step 1: Clone/Navigate to Project
```bash
cd c:\Users\benur\Desktop\skillnest_full_project_v4.css-update
```

### Step 2: Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### Step 3: Install Dependencies
```bash
pip install django pillow
```

### Step 4: Apply Database Migrations
```bash
python manage.py migrate
```

### Step 5: Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```
Follow the prompts to create an admin account with:
- Username: (your choice)
- Email: (your choice)
- Password: (your choice)

### Step 6: Initialize Sample Data
```bash
python manage.py shell
# Then copy-paste the contents of setup.py or run:
# Get-Content setup.py | python manage.py shell  (Windows)
```

This creates:
- 14 Skills across different categories
- 4 Career Paths with skill requirements
- 6 Sample Courses with lessons
- 3 Sample Job listings
- Test Teacher account (username: teacher1, password: teacher123)

### Step 7: Start Development Server
```bash
python manage.py runserver
```

The platform will be available at: **http://localhost:8000**

## Testing the Platform

### 1. **Student Flow**
```
1. Go to http://localhost:8000
2. Click "Signup" → Select "Student" role
3. Create account and login
4. Browse courses at /courses
5. Enroll in a course
6. Mark lessons as complete to earn certificate
7. View job recommendations at /recommended-jobs
8. Check skill gap analysis at /skill-gap
9. Share your portfolio at /portfolio/<username>
```

### 2. **Teacher Account**
```
Username: teacher1
Password: teacher123
Access: http://localhost:8000/login
Dashboard: http://localhost:8000/dashboard
```

### 3. **Admin Panel**
```
1. Login with superuser credentials at http://localhost:8000/login
2. Access admin panel at http://localhost:8000/admin
3. Manage all models: Users, Courses, Jobs, Skills, etc.
```

## Project Structure

```
skillnest_full_project_v4.css-update/
├── manage.py                           # Django management script
├── setup.py                            # Initial data setup script
├── db.sqlite3                          # SQLite database
├── skillnest/                          # Main project config
│   ├── settings.py                     # Project settings
│   ├── urls.py                         # Main URL routing
│   ├── wsgi.py                         # WSGI config
│   └── asgi.py                         # ASGI config
├── skillnest_app/                      # Main Django app
│   ├── models.py                       # Database models
│   ├── views.py                        # Views (Controllers)
│   ├── urls.py                         # App URL routing
│   ├── admin.py                        # Admin interface config
│   ├── recommendations.py              # Job recommendation engine
│   ├── tests.py                        # Unit tests
│   ├── migrations/                     # Database migrations
│   └── templates/skillnest_app/        # HTML templates
│       ├── base.html                   # Base template with navbar
│       ├── home.html                   # Home page
│       ├── login.html                  # Login page
│       ├── signup.html                 # Registration page
│       ├── profile.html                # User profile
│       ├── courses.html                # Course listing
│       ├── course_detail.html          # Course detail & enrollment
│       ├── student_dashboard.html      # Student dashboard
│       ├── teacher_dashboard.html      # Teacher dashboard
│       ├── admin_dashboard.html        # Admin dashboard
│       ├── jobs.html                   # Job listings
│       ├── job_detail.html             # Job details
│       ├── recommended_jobs.html       # AI recommendations
│       ├── portfolio.html              # Student portfolio
│       ├── certificate.html            # Certificate view
│       ├── skill_gap.html              # Skill gap analysis
│       ├── teachers.html               # Teachers listing
│       ├── teacher_profile.html        # Teacher profile
│       ├── about.html                  # About page
│       └── contact.html                # Contact page
└── static/                             # Static files (CSS, JS, Images)
```

## Database Models

### Core Models
- **User** (Django's built-in)
  - Extended with UserProfile for roles
  
- **UserProfile**
  - role: student, teacher, admin
  - bio, profile_picture, phone

- **Skill**
  - skill_name, description, category

- **Course**
  - title, description, category, level
  - instructor (FK to User)
  - skills (M2M with Skill)
  - duration_hours

- **Lesson**
  - course (FK)
  - title, description, content
  - video_url, duration_minutes
  - order

- **Enrollment**
  - user (FK), course (FK)
  - progress_percent, status
  - completed_lessons (M2M)
  - enroll_date, completed_date

- **StudentSkill**
  - user (FK), skill (FK)
  - proficiency_level

- **Certificate**
  - user (FK), course (FK)
  - issue_date, certificate_code

- **Job**
  - job_title, company_name, location
  - description, requirements
  - salary_min, salary_max, job_type
  - skills_required (M2M)
  - posted_by (FK to User)
  - last_date, is_active

- **JobRecommendation**
  - user (FK), job (FK)
  - match_score, matched_skills_count
  - total_required_skills

- **CareerPath**
  - career_name, description
  - required_skills (M2M)
  - experience_level

## Key Features Explained

### 1. Job Recommendation Engine (`recommendations.py`)
```python
# Simple rule-based matching algorithm
match_score = (matched_skills / total_required_skills) * 100

Example:
- Student has: Python, Django, SQL (3 skills)
- Job requires: Python, Django, SQL, JavaScript (4 skills)
- Match Score: 3/4 = 75%
```

### 2. Progress Tracking
- Automatic progress calculation based on completed lessons
- Auto-award skills when course is 100% complete
- Auto-generate certificates with unique codes

### 3. Public Portfolio
- Accessible at: `/portfolio/<username>/`
- Shareable link showing:
  - Profile info (name, bio, picture)
  - Completed courses
  - Earned certificates
  - Skills with proficiency levels

### 4. Skill Gap Analysis
- Select target career path
- View required skills
- Identify missing skills
- Links to relevant courses

## API Endpoints

### Public Routes
- `GET /` - Home page
- `GET /courses` - Course listing with filters
- `GET /courses/<id>/` - Course detail
- `GET /jobs` - Job listings
- `GET /jobs/<id>/` - Job detail
- `GET /portfolio/<username>/` - Public portfolio
- `GET /teachers` - Teachers listing
- `GET /about` - About page
- `GET /contact` - Contact page

### Authentication Routes
- `POST /signup` - User registration
- `POST /login` - User login
- `GET /logout` - User logout
- `GET /profile` - User profile (edit form)
- `POST /profile` - Update profile

### Student Routes (Login Required)
- `GET /dashboard` - Student dashboard
- `POST /courses/<id>/enroll/` - Enroll course
- `POST /lessons/<id>/complete/` - Mark lesson complete
- `GET /recommended-jobs` - AI job recommendations
- `GET /skill-gap` - Skill gap analysis
- `GET /certificate/<id>/` - View certificate

### Admin Routes
- `GET /admin` - Django admin panel
- `POST` Various admin operations

## Customization

### Adding New Skills
Go to Django admin: `/admin/skillnest_app/skill/`

### Adding New Courses
1. Login as teacher
2. Go to admin: `/admin/skillnest_app/course/`
3. Create course and add lessons

### Adding Job Postings
1. Login as admin
2. Go to admin: `/admin/skillnest_app/job/`
3. Create job and specify required skills

### Modifying Styles
Edit: `skillnest_app/templates/skillnest_app/base.html`
Look for the `<style>` tag with CSS variables:
```css
--primary-color: #2563eb;
--secondary-color: #7c3aed;
--success-color: #10b981;
```

## Production Deployment

### Before Going Live:
1. Set `DEBUG = False` in `settings.py`
2. Set secure `SECRET_KEY`
3. Configure `ALLOWED_HOSTS`
4. Use production database (MySQL/PostgreSQL)
5. Set up email backend for notifications
6. Collect static files: `python manage.py collectstatic`
7. Use Gunicorn/uWSGI for app server
8. Use Nginx as reverse proxy

### Deploy to Heroku:
```bash
heroku create skillnest-app
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

## Troubleshooting

### Issue: Static files not loading
**Solution**: Create `static/` folder
```bash
mkdir static
python manage.py collectstatic --noinput
```

### Issue: Database locked
**Solution**: Delete `db.sqlite3` and re-run migrations
```bash
python manage.py migrate
```

### Issue: Port 8000 already in use
**Solution**: Use different port
```bash
python manage.py runserver 8001
```

## Future Enhancements

- [ ] Live video streaming for courses
- [ ] Interactive code editor for practice
- [ ] Discussion forums per course
- [ ] Email notifications
- [ ] Mobile app
- [ ] Advanced ML recommendation engine
- [ ] Payment integration for advanced courses
- [ ] Peer review and mentoring system
- [ ] Job interviews tracking
- [ ] Advanced analytics dashboard

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - Feel free to use this for personal or commercial projects.

## Support

For issues and questions:
- Create an issue on GitHub
- Email: support@skillnest.com
- Discord: [Join our community]

## Acknowledgments

- Django community
- Bootstrap for responsive design
- FontAwesome for icons
- All contributors

---

**SkillNest** - Empowering the next generation of tech professionals! 🚀
