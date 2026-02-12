from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ==================== USER PROFILE ====================
class UserProfile(models.Model):
    """Extended user profile with role information"""
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin/HR'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, default='profile_pics/default.jpg')
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Teacher-specific fields
    specialization = models.CharField(max_length=100, blank=True, null=True)
    expertise = models.TextField(blank=True, null=True)
    experience_years = models.PositiveIntegerField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


# Create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# ==================== SKILL ====================
class Skill(models.Model):
    """Skills that students can earn through courses"""
    skill_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['skill_name']
    
    def __str__(self):
        return self.skill_name


# ==================== COURSE ====================
class Course(models.Model):
    """Courses offered on SkillNest"""
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    CATEGORY_CHOICES = [
        ('web_dev', 'Web Development'),
        ('programming', 'Programming'),
        ('databases', 'Databases'),
        ('cloud', 'Cloud Computing'),
        ('data_science', 'Data Science'),
        ('mobile', 'Mobile Development'),
        ('devops', 'DevOps'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught')
    cover_image = models.ImageField(upload_to='course_covers/', blank=True, null=True)
    skills = models.ManyToManyField(Skill, related_name='courses')
    duration_hours = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_enrolled_count(self):
        return self.enrollments.filter(status='in_progress').count()


# ==================== COURSE LESSON ====================
class Lesson(models.Model):
    """Individual lessons within a course"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    video_url = models.URLField(blank=True, null=True, verbose_name='Video Embed URL')
    video_file = models.FileField(upload_to='lesson_videos/', blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    duration_minutes = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


# ==================== ENROLLMENT ====================
class Enrollment(models.Model):
    """Student enrollment in courses"""
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enroll_date = models.DateTimeField(auto_now_add=True)
    progress_percent = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    completed_lessons = models.ManyToManyField(Lesson, blank=True, related_name='completed_by')
    completed_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-enroll_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
    def update_progress(self):
        """Update progress percentage based on completed lessons"""
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            self.progress_percent = 100
        else:
            completed = self.completed_lessons.count()
            self.progress_percent = (completed / total_lessons) * 100
        self.save()


# ==================== STUDENT SKILL ====================
class StudentSkill(models.Model):
    """Skills a student has gained"""
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='student_skills')
    proficiency_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    acquired_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'skill')
    
    def __str__(self):
        return f"{self.user.username} - {self.skill.skill_name}"


# ==================== CERTIFICATE ====================
class Certificate(models.Model):
    """Certificate awarded upon course completion"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    issue_date = models.DateTimeField(auto_now_add=True)
    certificate_code = models.CharField(max_length=50, unique=True)
    
    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"Certificate: {self.user.username} - {self.course.title}"


# ==================== JOB ====================
class Job(models.Model):
    """Job openings posted by HR/Admin"""
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    salary_min = models.IntegerField(blank=True, null=True)
    salary_max = models.IntegerField(blank=True, null=True)
    job_type = models.CharField(max_length=50, choices=[('full_time', 'Full Time'), ('part_time', 'Part Time'), ('contract', 'Contract')], default='full_time')
    requirements = models.TextField()
    skills_required = models.ManyToManyField(Skill, related_name='jobs_requiring')
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs_posted')
    posted_date = models.DateTimeField(auto_now_add=True)
    last_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-posted_date']
    
    def __str__(self):
        return f"{self.job_title} at {self.company_name}"


# ==================== JOB RECOMMENDATION ====================
class JobRecommendation(models.Model):
    """AI-powered job recommendations based on student skills"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_recommendations')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='recommendations')
    match_score = models.FloatField()  # 0.0 to 1.0
    matched_skills_count = models.IntegerField()
    total_required_skills = models.IntegerField()
    recommended_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-match_score', '-recommended_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.job.job_title} ({self.match_score:.0%})"


# ==================== CAREER PATH ====================
class CareerPath(models.Model):
    """Predefined career paths with required skills"""
    career_name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    required_skills = models.ManyToManyField(Skill, related_name='career_paths')
    experience_level = models.CharField(max_length=20, choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['career_name']
    
    def __str__(self):
        return self.career_name


# ==================== PORTFOLIO PROJECTS ====================
class PortfolioProject(models.Model):
    """Student's project showcases"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolio_projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    technologies = models.ManyToManyField(Skill, related_name='projects_using')
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    live_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


# ==================== WORK EXPERIENCE ====================
class WorkExperience(models.Model):
    """Student's work experience"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_experiences')
    company_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    skills_used = models.ManyToManyField(Skill, related_name='work_experiences_using')
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.job_title} at {self.company_name}"


# ==================== EDUCATION ====================
class Education(models.Model):
    """Student's educational background"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='education')
    school_name = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    grade = models.CharField(max_length=10, blank=True, null=True)
    activities = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.degree} from {self.school_name}"


# ==================== SOCIAL LINKS ====================
class SocialLink(models.Model):
    """Student's social media and professional links"""
    PLATFORM_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('github', 'GitHub'),
        ('twitter', 'Twitter'),
        ('portfolio', 'Portfolio Website'),
        ('website', 'Personal Website'),
        ('instagram', 'Instagram'),
        ('dribbble', 'Dribbble'),
        ('behance', 'Behance'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_links')
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    url = models.URLField()
    display_name = models.CharField(max_length=100, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'platform')
        ordering = ['platform']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_platform_display()}"


# ==================== TESTIMONIALS ====================
class Testimonial(models.Model):
    """Testimonials and recommendations for students"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='testimonials_received')
    given_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='testimonials_given')
    content = models.TextField()
    rating = models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
    relationship = models.CharField(max_length=50, choices=[
        ('instructor', 'Instructor'),
        ('colleague', 'Colleague'),
        ('manager', 'Manager'),
        ('client', 'Client'),
        ('other', 'Other')
    ], default='colleague')
    is_approved = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.given_by.username} → {self.user.username}"


# ==================== ACHIEVEMENT BADGES ====================
class AchievementBadge(models.Model):
    """Predefined achievement badges"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/', blank=True, null=True)
    badge_type = models.CharField(max_length=50, choices=[
        ('skill_master', 'Skill Master'),
        ('course_completion', 'Course Completion'),
        ('speed_learner', 'Speed Learner'),
        ('consistency', 'Consistency'),
        ('streak', 'Learning Streak'),
        ('milestone', 'Milestone'),
        ('other', 'Other')
    ])
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


# ==================== USER BADGES ====================
class UserBadge(models.Model):
    """Badges earned by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(AchievementBadge, on_delete=models.CASCADE)
    earned_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'badge')
        ordering = ['-earned_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


# ==================== CONTACT MESSAGE ====================
class ContactMessage(models.Model):
    """Contact form submissions from users"""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300, blank=True, null=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject or 'No Subject'}"
    
    def mark_resolved(self):
        """Mark this message as resolved"""
        from django.utils import timezone
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.save()
