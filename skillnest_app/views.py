from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count, F
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from datetime import datetime, timedelta
import hashlib
import uuid
from django.templatetags.static import static

from .models import (
    UserProfile, Course, Enrollment, Skill, Certificate,
    Lesson, StudentSkill, Job, JobRecommendation, CareerPath
)
from .recommendations import get_job_recommendations, calculate_match_score
from .decorators import teacher_required
from .forms import CourseCreateForm
from .forms import LessonForm


# ==================== HOME VIEW ====================
def home(request):
    """Home page with featured courses and categories"""
    # Redirect admin users to admin dashboard
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        if request.user.profile.role == 'admin':
            return redirect('admin_dashboard')
        elif request.user.profile.role == 'teacher':
            return redirect('dashboard')
    
    featured_courses = Course.objects.all()[:6]
    categories = Course.CATEGORY_CHOICES
    skills_count = Skill.objects.count()
    courses_count = Course.objects.count()
    total_students = User.objects.filter(profile__role='student').count()
    
    context = {
        'trending_courses': featured_courses,
        'categories': categories,
        'skills_count': skills_count,
        'courses_count': courses_count,
        'total_students': total_students,
    }
    return render(request, 'skillnest_app/home_merged.html', context)


# ==================== AUTHENTICATION VIEWS ====================
@require_http_methods(["GET", "POST"])
def signup(request):
    """User signup with role selection"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        role = request.POST.get('role', 'student')
        
        # Validation
        if not all([username, email, password, password_confirm]):
            messages.error(request, 'All fields are required.')
            return render(request, 'skillnest_app/signup_merged.html', {'role': role})
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'skillnest_app/signup_merged.html', {'role': role})
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'skillnest_app/signup_merged.html', {'role': role})
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'skillnest_app/signup_merged.html', {'role': role})
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'skillnest_app/signup_merged.html', {'role': role})
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Ensure profile exists and set role
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.save()
        
        messages.success(request, 'Signup successful! Please login.')
        return redirect('login')
    
    # Filter out admin role from signup options
    available_roles = [role for role in UserProfile.ROLE_CHOICES if role[0] != 'admin']
    
    context = {
        'roles': available_roles,
        'default_role': 'student'
    }
    return render(request, 'skillnest_app/signup_merged.html', context)


@require_http_methods(["GET", "POST"])
def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'skillnest_app/login_merged.html')


@login_required(login_url='login')
def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required(login_url='login')
def profile(request):
    """User profile view and edit"""
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        profile.bio = request.POST.get('bio', profile.bio)
        profile.phone = request.POST.get('phone', profile.phone)
        
        # Handle teacher specialization
        if profile.role == 'teacher':
            profile.specialization = request.POST.get('specialization', profile.specialization)
        
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        user.save()
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    # Add teacher-specific context if user is a teacher
    teacher_context = {}
    if profile.role == 'teacher':
        courses = Course.objects.filter(instructor=user)
        total_lessons = sum(course.lessons.count() for course in courses)
        total_students = Enrollment.objects.filter(course__instructor=user).count()
        teacher_context = {
            'total_lessons': total_lessons,
            'total_students': total_students,
        }
    
    context = {
        'profile_user': user,
        'user_profile': profile,
        'is_owner': True,
        'enrolled_courses': Enrollment.objects.filter(user=user),
        'certificates': Certificate.objects.filter(user=user),
    }
    context.update(teacher_context)
    return render(request, 'skillnest_app/profile_merged.html', context)


# ==================== DASHBOARD ====================
@login_required(login_url='login')
def dashboard(request):
    """User dashboard based on role"""
    print("DEBUG: Dashboard view called")
    user = request.user
    
    # Ensure profile exists
    try:
        role = user.profile.role
    except:
        from .models import UserProfile
        profile = UserProfile.objects.create(user=user)
        role = profile.role
    
    if role == 'student':
        enrollments = Enrollment.objects.filter(user=user)
        certificates = Certificate.objects.filter(user=user)
        skills = StudentSkill.objects.filter(user=user)
        
        context = {
            'enrollments': enrollments,
            'certificates': certificates,
            'skills': skills,
        }
        return render(request, 'skillnest_app/student_dashboard_merged.html', context)
    
    elif role == 'teacher':
        print("DEBUG: Teacher role detected")
        courses = Course.objects.filter(instructor=user)
        total_enrollments = Enrollment.objects.filter(course__instructor=user).count()
        
        # Handle profile update POST request
        if request.method == 'POST' and 'update_profile' in request.POST:
            print("DEBUG: Profile update POST request received")
            print("DEBUG: POST data:", dict(request.POST))
            print("DEBUG: FILES:", list(request.FILES.keys()))
            
            try:
                user.first_name = request.POST.get('first_name', user.first_name)
                user.last_name = request.POST.get('last_name', user.last_name)
                user.email = request.POST.get('email', user.email)
                user.profile.bio = request.POST.get('bio', user.profile.bio)
                user.profile.phone = request.POST.get('phone', user.profile.phone)
                
                # Handle teacher-specific fields
                if user.profile.role == 'teacher':
                    user.profile.specialization = request.POST.get('specialization', user.profile.specialization)
                    user.profile.expertise = request.POST.get('expertise', user.profile.expertise)
                    experience_years = request.POST.get('experience_years')
                    if experience_years:
                        try:
                            user.profile.experience_years = int(experience_years)
                        except ValueError:
                            pass  # Keep existing value if invalid
                
                if 'profile_picture' in request.FILES:
                    user.profile.profile_picture = request.FILES['profile_picture']
                    print("DEBUG: Profile picture uploaded")
                
                user.save()
                user.profile.save()
                print("DEBUG: Profile saved successfully")
                messages.success(request, 'Profile updated successfully!')
                # For debugging, return a simple response instead of redirect
                from django.http import HttpResponse
                return HttpResponse("Profile updated successfully! <a href='/dashboard/'>Back to Dashboard</a>")
            except Exception as e:
                print("DEBUG: Error saving profile:", str(e))
                messages.error(request, f'Error updating profile: {str(e)}')
                return redirect('dashboard')
        
        context = {
            'courses': courses,
            'total_enrollments': total_enrollments,
        }
        return render(request, 'skillnest_app/teacher_dashboard_merged.html', context)
    
    elif role == 'admin':
        # Redirect admin users to the admin panel
        return redirect('admin_dashboard')
    
    return redirect('home')


# Teacher: create course
@teacher_required
def teacher_create_course(request):
    if request.method == 'POST':
        form = CourseCreateForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            form.save_m2m()

            # create an initial lesson if provided (file prioritized over URL)
            title = form.cleaned_data.get('initial_lesson_title')
            video_file = form.cleaned_data.get('initial_lesson_video_file')
            video_url = form.cleaned_data.get('initial_lesson_video_url') if 'initial_lesson_video_url' in form.cleaned_data else None
            if title or video_file or video_url:
                Lesson.objects.create(
                    course=course,
                    title=title or 'Introduction',
                    video_file=video_file if video_file else None,
                    video_url=video_url if not video_file else None,
                )

            messages.success(request, 'Course created successfully.')
            return redirect('dashboard')
    else:
        form = CourseCreateForm()
    return render(request, 'skillnest_app/teacher/course_form.html', {'form': form, 'action': 'Create'})


# Teacher: edit course
@teacher_required
def teacher_edit_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if course.instructor != request.user:
        messages.error(request, 'Not authorized to edit this course.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = CourseCreateForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated.')
            return redirect('teacher_course_management')
    else:
        form = CourseCreateForm(instance=course)
    return render(request, 'skillnest_app/teacher/course_form.html', {'form': form, 'action': 'Edit', 'course': course})


# Teacher: delete course
@teacher_required
def teacher_delete_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if course.instructor != request.user:
        messages.error(request, 'Not authorized to delete this course.')
        return redirect('dashboard')

    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted.')
        return redirect('teacher_course_management')
    return render(request, 'skillnest_app/teacher/course_confirm_delete.html', {'course': course})


# Lesson CRUD for teachers
@teacher_required
def teacher_add_lesson(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if course.instructor != request.user:
        messages.error(request, 'Not authorized to add lessons to this course.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, 'Lesson added.')
            return redirect('dashboard')
    else:
        form = LessonForm()
    return render(request, 'skillnest_app/lesson_form_merged.html', {'form': form, 'course': course, 'action': 'Add'})


@teacher_required
def teacher_edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    if lesson.course.instructor != request.user:
        messages.error(request, 'Not authorized to edit this lesson.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson updated.')
            return redirect('dashboard')
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'skillnest_app/lesson_form_merged.html', {'form': form, 'course': lesson.course, 'action': 'Edit'})


@teacher_required
def teacher_delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    if lesson.course.instructor != request.user:
        messages.error(request, 'Not authorized to delete this lesson.')
        return redirect('dashboard')

    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lesson deleted.')
        return redirect('dashboard')
    return render(request, 'skillnest_app/lesson_confirm_delete_merged.html', {'lesson': lesson})


# Teacher: course students
@teacher_required
def teacher_course_students(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if course.instructor != request.user:
        messages.error(request, 'Not authorized to view students for this course.')
        return redirect('dashboard')

    enrollments = Enrollment.objects.filter(course=course).select_related('user')
    return render(request, 'skillnest_app/teacher/course_students.html', {'course': course, 'enrollments': enrollments})


# Teacher: course management page
@teacher_required
def teacher_course_management(request):
    courses = Course.objects.filter(instructor=request.user).prefetch_related('lessons')
    return render(request, 'skillnest_app/teacher_course_management.html', {'courses': courses})


# ==================== COURSES ====================
def courses(request):
    """List all courses with filters"""
    courses_list = Course.objects.all()
    # Provide a deterministic fallback image per instructor using images/pic-1..pic-9.jpg
    fallback_names = [f'images/pic-{i}.jpg' for i in range(1, 10)]
    total = len(fallback_names) or 1
    for course in courses_list:
        instructor = getattr(course, 'instructor', None)
        # choose index from instructor id if available, else from username hash
        try:
            if instructor and getattr(instructor, 'id', None) is not None:
                key = int(instructor.id)
            elif instructor and getattr(instructor, 'username', None):
                key = abs(hash(instructor.username))
            else:
                key = id(course)
            idx = int(key) % total
            course.fallback_image = static(fallback_names[idx])
        except Exception:
            course.fallback_image = static('images/pic-2.jpg')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        courses_list = courses_list.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by category
    category = request.GET.get('category', '')
    if category:
        courses_list = courses_list.filter(category=category)
    
    # Filter by level
    level = request.GET.get('level', '')
    if level:
        courses_list = courses_list.filter(level=level)
    
    context = {
        'courses': courses_list,
        'categories': Course.CATEGORY_CHOICES,
        'levels': Course.LEVEL_CHOICES,
        'search_query': search_query,
        'selected_category': category,
        'selected_level': level,
    }
    return render(request, 'skillnest_app/courses_merged.html', context)


def course_detail(request, course_id):
    """Course detail page"""
    course = get_object_or_404(Course, pk=course_id)
    lessons = course.lessons.all()
    skills = course.skills.all()
    enrollment = None
    is_enrolled = False
    # Handle POST actions from the course detail page: enroll or mark lesson complete
    if request.method == 'POST':
        # Enroll action (form with name 'enroll')
        if request.POST.get('enroll') is not None:
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to enroll in the course.')
                return redirect('login')
            user = request.user
            if Enrollment.objects.filter(user=user, course=course).exists():
                messages.warning(request, 'You are already enrolled in this course.')
            else:
                Enrollment.objects.create(user=user, course=course)
                messages.success(request, f'Successfully enrolled in {course.title}!')
            return redirect('course_detail', course_id=course_id)

        # Save playlist action (placeholder for future implementation)
        if request.POST.get('save_playlist') is not None:
            messages.info(request, 'Course saving feature coming soon!')
            return redirect('course_detail', course_id=course_id)
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to mark lessons as complete.')
                return redirect('login')
            lesson_id = request.POST.get('mark_complete')
            try:
                lesson = Lesson.objects.get(pk=int(lesson_id))
            except Exception:
                messages.error(request, 'Invalid lesson.')
                return redirect('course_detail', course_id=course_id)

            try:
                enrollment = Enrollment.objects.get(user=request.user, course=lesson.course)
            except Enrollment.DoesNotExist:
                messages.error(request, 'You need to enroll in the course before marking lessons complete.')
                return redirect('course_detail', course_id=course_id)

            enrollment.completed_lessons.add(lesson)
            enrollment.update_progress()

            # If course completed, set status, award skills and certificate
            if enrollment.progress_percent >= 100:
                enrollment.status = 'completed'
                enrollment.completed_date = datetime.now()
                enrollment.save()
                for skill in lesson.course.skills.all():
                    StudentSkill.objects.get_or_create(user=request.user, skill=skill)
                certificate_code = str(uuid.uuid4())[:8].upper()
                Certificate.objects.create(user=request.user, course=lesson.course, certificate_code=certificate_code)
                messages.success(request, f'Congratulations! You completed {lesson.course.title}! Certificate awarded.')
            else:
                messages.success(request, f'Lesson "{lesson.title}" marked as complete.')

            return redirect('course_detail', course_id=course_id)

    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        is_enrolled = enrollment is not None
        is_instructor = course.instructor == request.user
        
        # Calculate progress variables
        if enrollment:
            progress_percentage = enrollment.progress_percent
            completed_lessons = enrollment.completed_lessons.count()
            total_lessons = course.lessons.count()
        else:
            progress_percentage = 0
            completed_lessons = 0
            total_lessons = course.lessons.count()
        
        # Check if course is saved by user (placeholder for future implementation)
        is_saved = False  # TODO: Implement course saving functionality
    else:
        is_instructor = False
        progress_percentage = 0
        completed_lessons = 0
        total_lessons = course.lessons.count()
        is_saved = False
    
    context = {
        'course': course,
        'lessons': lessons,
        'skills': skills,
        'enrollment': enrollment,
        'is_enrolled': is_enrolled,
        'is_instructor': is_instructor,
        'progress_percentage': progress_percentage,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'is_saved': is_saved,
    }
    return render(request, 'skillnest_app/course_detail_merged.html', context)


@login_required
def watch_lesson(request, course_id, lesson_id):
    """Lesson watching page with video player and completion button"""
    course = get_object_or_404(Course, pk=course_id)
    lesson = get_object_or_404(Lesson, pk=lesson_id, course=course)
    
    # Check if user is enrolled
    try:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
        is_enrolled = True
    except Enrollment.DoesNotExist:
        messages.error(request, 'You need to enroll in this course to watch lessons.')
        return redirect('course_detail', course_id=course_id)
    
    # Handle lesson completion
    if request.method == 'POST' and request.POST.get('mark_complete'):
        if lesson not in enrollment.completed_lessons.all():
            enrollment.completed_lessons.add(lesson)
            enrollment.update_progress()
            
            # Check if course is completed
            if enrollment.progress_percent >= 100:
                enrollment.status = 'completed'
                enrollment.completed_date = datetime.now()
                enrollment.save()
                
                # Award skills and certificate
                for skill in course.skills.all():
                    StudentSkill.objects.get_or_create(user=request.user, skill=skill)
                certificate_code = str(uuid.uuid4())[:8].upper()
                Certificate.objects.create(user=request.user, course=course, certificate_code=certificate_code)
                messages.success(request, f'Congratulations! You completed {course.title}! Certificate awarded.')
            else:
                messages.success(request, f'Lesson "{lesson.title}" marked as complete.')
        
        return redirect('course_detail', course_id=course_id)
    
    # Check if lesson is already completed
    is_completed = lesson in enrollment.completed_lessons.all()
    
    # Calculate progress variables for the template
    progress_percentage = enrollment.progress_percent
    completed_lessons = enrollment.completed_lessons.count()
    total_lessons = course.lessons.count()
    
    # Calculate current lesson number
    current_lesson_number = list(course.lessons.order_by('id')).index(lesson) + 1
    
    # Get completed lesson IDs for the sidebar
    completed_lesson_ids = [lesson.id for lesson in enrollment.completed_lessons.all()]
    
    # Get previous and next lessons
    lessons_list = list(course.lessons.order_by('id'))
    lesson_index = lessons_list.index(lesson)
    previous_lesson = lessons_list[lesson_index - 1] if lesson_index > 0 else None
    next_lesson = lessons_list[lesson_index + 1] if lesson_index < len(lessons_list) - 1 else None
    
    # Calculate SVG stroke-dasharray for circular progress (339 is circumference)
    progress_stroke_dasharray = progress_percentage * 3.39
    
    context = {
        'course': course,
        'lesson': lesson,
        'is_completed': is_completed,
        'enrollment': enrollment,
        'progress_percentage': progress_percentage,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'current_lesson_number': current_lesson_number,
        'completed_lesson_ids': completed_lesson_ids,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
        'progress_stroke_dasharray': progress_stroke_dasharray,
    }
    return render(request, 'skillnest_app/watch_lesson.html', context)


@login_required(login_url='login')
def enroll_course(request, course_id):
    """Enroll a student in a course"""
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    
    # Check if already enrolled
    if Enrollment.objects.filter(user=user, course=course).exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('course_detail', course_id=course_id)
    
    # Create enrollment
    enrollment = Enrollment.objects.create(user=user, course=course)
    messages.success(request, f'Successfully enrolled in {course.title}!')
    
    return redirect('course_detail', course_id=course_id)


@login_required(login_url='login')
def mark_lesson_complete(request, lesson_id):
    """Mark a lesson as completed"""
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    user = request.user
    
    enrollment = get_object_or_404(Enrollment, user=user, course=lesson.course)
    
    # Add lesson to completed
    enrollment.completed_lessons.add(lesson)
    enrollment.update_progress()
    
    # Check if course is completed (100%)
    if enrollment.progress_percent >= 100:
        enrollment.status = 'completed'
        enrollment.completed_date = datetime.now()
        enrollment.save()
        
        # Award skills from course
        for skill in lesson.course.skills.all():
            StudentSkill.objects.get_or_create(user=user, skill=skill)
        
        # Create certificate
        certificate_code = str(uuid.uuid4())[:8].upper()
        Certificate.objects.create(
            user=user,
            course=lesson.course,
            certificate_code=certificate_code
        )
        
        messages.success(request, f'Congratulations! You completed {lesson.course.title}! Certificate awarded.')
    else:
        messages.success(request, f'Lesson "{lesson.title}" marked as complete.')
    
    return redirect('course_detail', course_id=lesson.course.id)


# ==================== PORTFOLIO ====================
def portfolio(request, username):
    """Public portfolio page"""
    from .models import PortfolioProject, WorkExperience, Education, SocialLink, UserBadge
    
    user = get_object_or_404(User, username=username)
    profile = user.profile
    
    if profile.role != 'student':
        return redirect('home')
    
    certificates = Certificate.objects.filter(user=user)
    skills = StudentSkill.objects.filter(user=user)
    courses = Course.objects.filter(
        enrollments__user=user,
        enrollments__status='completed'
    ).distinct()
    projects = PortfolioProject.objects.filter(user=user)
    experiences = WorkExperience.objects.filter(user=user)
    education = Education.objects.filter(user=user)
    social_links = SocialLink.objects.filter(user=user)
    badges = UserBadge.objects.filter(user=user)
    
    # Calculate stats
    total_courses = Enrollment.objects.filter(user=user).count()
    in_progress = Enrollment.objects.filter(user=user, status='in_progress').count()
    
    context = {
        'portfolio_user': user,
        'profile': profile,
        'certificates': certificates,
        'skills': skills,
        'completed_courses': courses,
        'projects': projects,
        'experiences': experiences,
        'education': education,
        'social_links': social_links,
        'badges': badges,
        'total_courses': total_courses,
        'in_progress': in_progress,
    }
    return render(request, 'skillnest_app/portfolio_merged.html', context)


# ==================== CERTIFICATES ====================
@login_required(login_url='login')
def certificate_view(request, certificate_id):
    """View and download certificate"""
    certificate = get_object_or_404(Certificate, pk=certificate_id)
    
    # Check if user can view
    if request.user != certificate.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this certificate.')
        return redirect('home')
    
    context = {
        'certificate': certificate,
        'user': certificate.user,
        'course': certificate.course,
    }
    return render(request, 'skillnest_app/certificate_merged.html', context)


# ==================== JOBS ====================
def jobs(request):
    """List all job openings"""
    jobs_list = Job.objects.filter(is_active=True)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        jobs_list = jobs_list.filter(
            Q(job_title__icontains=search_query) |
            Q(company_name__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Calculate match score for authenticated users
    if request.user.is_authenticated:
        user_skills = set(StudentSkill.objects.filter(user=request.user).values_list('skill_id', flat=True))
        for job in jobs_list:
            required_skills = set(job.skills_required.values_list('id', flat=True))
            if required_skills:
                matched = len(user_skills & required_skills)
                job.match_percent = (matched / len(required_skills)) * 100
            else:
                job.match_percent = 0
    
    context = {
        'jobs': jobs_list,
        'search_query': search_query,
    }
    return render(request, 'skillnest_app/jobs_merged.html', context)


def job_detail(request, job_id):
    """Job detail page"""
    job = get_object_or_404(Job, pk=job_id)
    required_skills = job.skills_required.all()
    
    match_percent = 0
    if request.user.is_authenticated:
        user_skills = set(StudentSkill.objects.filter(user=request.user).values_list('skill_id', flat=True))
        required_skill_ids = set(required_skills.values_list('id', flat=True))
        if required_skill_ids:
            matched = len(user_skills & required_skill_ids)
            match_percent = (matched / len(required_skill_ids)) * 100
    
    context = {
        'job': job,
        'required_skills': required_skills,
        'match_percent': match_percent,
    }
    return render(request, 'skillnest_app/job_detail_merged.html', context)


# ==================== JOB RECOMMENDATIONS ====================
@login_required(login_url='login')
@login_required(login_url='login')
def recommended_jobs(request):
    """Get AI-powered job recommendations"""
    user = request.user
    
    # Get user's skills
    user_skills = StudentSkill.objects.filter(user=user).values_list('skill_id', flat=True)
    
    recommendations = []
    
    if user_skills:
        # Get recommendations
        rec_list = get_job_recommendations(user, list(user_skills))
        
        # Transform recommendation dicts to have job attributes accessible at top level
        recommendations = []
        for rec in rec_list:
            job = rec['job']
            # Add match info as properties on job object
            job.match_percentage = rec['match_percent']
            job.matched_skills_count = rec['matched_skills_count']
            job.missing_skills_count = rec['missing_skills_count']
            job.required_skills = job.skills_required.all()
            recommendations.append(job)
    
    context = {
        'recommendations': recommendations,
        'user_skills_count': len(user_skills),
    }
    return render(request, 'skillnest_app/recommended_jobs_merged.html', context)


# ==================== SKILL GAP ANALYSIS ====================
@login_required(login_url='login')
@login_required(login_url='login')
def skill_gap(request):
    """Analyze skill gap for target career"""
    user = request.user
    
    recommendations = None
    acquired_skills = []
    gap_skills_with_links = []
    recommended_courses = []
    
    if request.method == 'POST':
        career = request.POST.get('career', '')
        user_skills_str = request.POST.get('user_skills', '')

        if career and user_skills_str:
            # Parse user skills from textarea
            user_skills_input = [s.strip().lower() for s in user_skills_str.split(',') if s.strip()]

            # Define skill requirements for each career
            career_skills = {
                'Frontend Developer': ['HTML', 'CSS', 'JavaScript', 'React', 'TypeScript', 'UI/UX'],
                'Backend Developer': ['Python', 'Node.js', 'SQL', 'REST API', 'Docker', 'Database Design'],
                'Full Stack Developer': ['HTML', 'CSS', 'JavaScript', 'React', 'Node.js', 'SQL', 'Python'],
                'Data Scientist': ['Python', 'SQL', 'Statistics', 'Machine Learning', 'TensorFlow', 'Pandas'],
                'DevOps Engineer': ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux', 'Jenkins'],
                'Mobile Developer': ['React Native', 'Swift', 'Kotlin', 'Mobile UI', 'Firebase'],
                'UI/UX Designer': ['Figma', 'UI Design', 'UX Research', 'Prototyping', 'CSS'],
                'Cloud Architect': ['AWS', 'Azure', 'GCP', 'Architecture', 'Security'],
            }

            required = set(career_skills.get(career, []))
            acquired = set()

            # Match user skills with required skills
            for user_skill in user_skills_input:
                for req_skill in required:
                    if user_skill in req_skill.lower():
                        acquired.add(req_skill)
                        break

            gap = required - acquired

            acquired_skills = sorted(list(acquired))
            gap_skills = sorted(list(gap))

            # Create skill links with YouTube search URLs
            gap_skills_with_links = [
                {
                    'name': skill,
                    'youtube_url': f'https://www.youtube.com/results?search_query=learn+{skill.replace(" ", "+")}'
                }
                for skill in gap_skills
            ]

            # Get recommended courses for gap skills
            if gap_skills:
                recommended_courses = Course.objects.filter(
                    skills__skill_name__icontains=gap_skills[0] if gap_skills else ''
                ).distinct()[:5]

            # Build recommended_videos from the first lesson of each recommended course (if available)
            recommended_videos = []
            for course in recommended_courses:
                # Assume related_name 'lessons' on Course -> Lesson
                first_lesson = course.lessons.first()
                if first_lesson and getattr(first_lesson, 'video_url', None):
                    v = first_lesson.video_url.strip()
                    embed = None
                    embed_type = 'video'
                    # Detect YouTube watch links and convert to embed
                    if 'youtube.com/watch' in v or 'youtu.be/' in v:
                        vid = None
                        if 'v=' in v:
                            try:
                                vid = v.split('v=')[1].split('&')[0]
                            except Exception:
                                vid = None
                        elif 'youtu.be/' in v:
                            try:
                                vid = v.split('youtu.be/')[1].split('?')[0]
                            except Exception:
                                vid = None
                        if vid:
                            embed = f'https://www.youtube.com/embed/{vid}'
                            embed_type = 'youtube'
                    else:
                        # assume direct mp4 or hosted video link usable in <video>
                        embed = v

                    if embed:
                        recommended_videos.append({
                            'course': course,
                            'title': getattr(course, 'title', str(course)),
                            'embed_src': embed,
                            'embed_type': embed_type,
                        })

            # attach to context
            context_videos = recommended_videos

            recommendations = True
        else:
            context_videos = []
    else:
        context_videos = []
    
    context = {
        'recommendations': recommendations,
        'acquired_skills': acquired_skills,
        'gap_skills_with_links': gap_skills_with_links,
        'recommended_courses': recommended_courses,
        'recommended_videos': context_videos,
    }
    return render(request, 'skillnest_app/skill_gap_merged.html', context)


# ==================== TEACHERS ====================
def teachers(request):
    """List all teachers"""
    teachers_list = User.objects.filter(profile__role='teacher')
    
    # Add course count
    for teacher in teachers_list:
        teacher.course_count = teacher.courses_taught.count()
    
    context = {
        'teachers': teachers_list,
    }
    return render(request, 'skillnest_app/teachers_merged.html', context)


def teacher_profile(request, username):
    """Teacher profile page"""
    teacher = get_object_or_404(User, username=username)
    
    if teacher.profile.role != 'teacher':
        return redirect('home')
    
    courses = teacher.courses_taught.all()
    total_students = Enrollment.objects.filter(course__instructor=teacher).count()
    
    context = {
        'teacher': teacher,
        'courses': courses,
        'total_students': total_students,
    }
    return render(request, 'skillnest_app/teacher_profile_merged.html', context)


# ==================== ABOUT & CONTACT ====================
def about(request):
    """About page"""
    return render(request, 'skillnest_app/about_merged.html')


def contact(request):
    """Contact page"""
    from .models import ContactMessage
    
    if request.method == 'POST':
        # Save contact message
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
        
        messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
        return redirect('contact')
    
    return render(request, 'skillnest_app/contact_merged.html')


# ==================== ADMIN PANEL VIEWS ====================

@login_required(login_url='login')
def admin_dashboard(request):
    """Admin dashboard with platform statistics"""
    from .decorators import admin_required
    from .models import ContactMessage
    
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    # Calculate statistics
    total_users = User.objects.count()
    total_students = User.objects.filter(profile__role='student').count()
    total_teachers = User.objects.filter(profile__role='teacher').count()
    total_courses = Course.objects.count()
    total_certificates = Certificate.objects.count()
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(is_active=True).count()
    total_enrollments = Enrollment.objects.count()
    active_enrollments = Enrollment.objects.filter(status='in_progress').count()
    pending_contacts = ContactMessage.objects.filter(is_resolved=False).count()
    
    # Recent data
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_courses = Course.objects.order_by('-created_at')[:5]
    recent_certificates = Certificate.objects.order_by('-issue_date')[:5]
    
    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'total_certificates': total_certificates,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_enrollments': total_enrollments,
        'active_enrollments': active_enrollments,
        'pending_contacts': pending_contacts,
        'recent_users': recent_users,
        'recent_courses': recent_courses,
        'recent_certificates': recent_certificates,
    }
    return render(request, 'skillnest_app/admin_panel_dashboard.html', context)


@login_required(login_url='login')
def admin_users(request):
    """User management - list all users with filtering"""
    from .decorators import admin_required
    
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    users_list = User.objects.all().select_related('profile')
    
    # Filter by role
    role_filter = request.GET.get('role', '')
    if role_filter:
        users_list = users_list.filter(profile__role=role_filter)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        users_list = users_list.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    context = {
        'users': users_list,
        'role_filter': role_filter,
        'search_query': search_query,
    }
    return render(request, 'skillnest_app/admin_users.html', context)


@login_required(login_url='login')
def admin_toggle_user_status(request, user_id):
    """Toggle user active/inactive status"""
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.username} has been {status}.')
    
    return redirect('admin_users')


@login_required(login_url='login')
def admin_approve_teacher(request, user_id):
    """Approve a teacher account"""
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        # Set user as active and confirm teacher role
        user.is_active = True
        if hasattr(user, 'profile'):
            user.profile.role = 'teacher'
            user.profile.save()
        user.save()
        messages.success(request, f'Teacher {user.username} has been approved.')
    
    return redirect('admin_users')


@login_required(login_url='login')
def admin_courses(request):
    """Course management - view all courses"""
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    courses_list = Course.objects.all().select_related('instructor')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        courses_list = courses_list.filter(
            Q(title__icontains=search_query) |
            Q(instructor__username__icontains=search_query)
        )
    
    # Add enrollment count to each course
    for course in courses_list:
        course.enrollment_count = course.enrollments.count()
    
    context = {
        'courses': courses_list,
        'search_query': search_query,
    }
    return render(request, 'skillnest_app/admin_courses.html', context)


@login_required(login_url='login')
def admin_delete_course(request, course_id):
    """Delete a course (admin only)"""
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    course = get_object_or_404(Course, pk=course_id)
    
    if request.method == 'POST':
        course_title = course.title
        course.delete()
        messages.success(request, f'Course "{course_title}" has been deleted.')
        return redirect('admin_courses')
    
    context = {'course': course}
    return render(request, 'skillnest_app/admin_course_delete.html', context)


@login_required(login_url='login')
def admin_certificates(request):
    """Certificate management - view and verify certificates"""
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    certificates_list = Certificate.objects.all().select_related('user', 'course')
    
    # Search by certificate code or username
    search_query = request.GET.get('search', '')
    if search_query:
        certificates_list = certificates_list.filter(
            Q(certificate_code__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(course__title__icontains=search_query)
        )
    
    context = {
        'certificates': certificates_list,
        'search_query': search_query,
    }
    return render(request, 'skillnest_app/admin_certificates.html', context)


@login_required(login_url='login')
def admin_revoke_certificate(request, cert_id):
    """Revoke a certificate (optional feature)"""
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    certificate = get_object_or_404(Certificate, pk=cert_id)
    
    if request.method == 'POST':
        cert_code = certificate.certificate_code
        certificate.delete()
        messages.success(request, f'Certificate {cert_code} has been revoked.')
        return redirect('admin_certificates')
    
    context = {'certificate': certificate}
    return render(request, 'skillnest_app/admin_certificate_revoke.html', context)


@login_required(login_url='login')
def admin_jobs(request):
    """Job management - list all jobs"""
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    jobs_list = Job.objects.all().select_related('posted_by')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        jobs_list = jobs_list.filter(is_active=True)
    elif status_filter == 'inactive':
        jobs_list = jobs_list.filter(is_active=False)
    
    context = {
        'jobs': jobs_list,
        'status_filter': status_filter,
    }
    return render(request, 'skillnest_app/admin_jobs.html', context)


@login_required(login_url='login')
def admin_create_job(request):
    """Create a new job posting"""
    from .forms import JobForm
    
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Job posting created successfully.')
            return redirect('admin_jobs')
    else:
        form = JobForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'skillnest_app/admin_job_form.html', context)


@login_required(login_url='login')
def admin_edit_job(request, job_id):
    """Edit an existing job posting"""
    from .forms import JobForm
    
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    job = get_object_or_404(Job, pk=job_id)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job posting updated successfully.')
            return redirect('admin_jobs')
    else:
        form = JobForm(instance=job)
    
    context = {
        'form': form,
        'job': job,
        'action': 'Edit',
    }
    return render(request, 'skillnest_app/admin_job_form.html', context)


@login_required(login_url='login')
def admin_delete_job(request, job_id):
    """Delete a job posting"""
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    job = get_object_or_404(Job, pk=job_id)
    
    if request.method == 'POST':
        job_title = job.job_title
        job.delete()
        messages.success(request, f'Job "{job_title}" has been deleted.')
        return redirect('admin_jobs')
    
    context = {'job': job}
    return render(request, 'skillnest_app/admin_job_delete.html', context)


@login_required(login_url='login')
def admin_toggle_job_status(request, job_id):
    """Toggle job active/inactive status"""
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    job = get_object_or_404(Job, pk=job_id)
    
    if request.method == 'POST':
        job.is_active = not job.is_active
        job.save()
        status = 'activated' if job.is_active else 'deactivated'
        messages.success(request, f'Job "{job.job_title}" has been {status}.')
    
    return redirect('admin_jobs')


@login_required(login_url='login')
def admin_skills(request):
    """Skill management - list all skills"""
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    skills_list = Skill.objects.all()
    
    # Add usage statistics
    for skill in skills_list:
        skill.student_count = StudentSkill.objects.filter(skill=skill).count()
        skill.course_count = skill.courses.count()
        skill.job_count = skill.jobs_requiring.count()
        skill.total_usage = skill.student_count + skill.course_count + skill.job_count
    
    context = {
        'skills': skills_list,
    }
    return render(request, 'skillnest_app/admin_skills.html', context)


@login_required(login_url='login')
def admin_create_skill(request):
    """Create a new skill"""
    from .forms import SkillForm
    
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill created successfully.')
            return redirect('admin_skills')
    else:
        form = SkillForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'skillnest_app/admin_skill_form.html', context)


@login_required(login_url='login')
def admin_edit_skill(request, skill_id):
    """Edit an existing skill"""
    from .forms import SkillForm
    
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    skill = get_object_or_404(Skill, pk=skill_id)
    
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill updated successfully.')
            return redirect('admin_skills')
    else:
        form = SkillForm(instance=skill)
    
    context = {
        'form': form,
        'skill': skill,
        'action': 'Edit',
    }
    return render(request, 'skillnest_app/admin_skill_form.html', context)


@login_required(login_url='login')
def admin_delete_skill(request, skill_id):
    """Delete a skill"""
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    skill = get_object_or_404(Skill, pk=skill_id)
    
    # Check if skill is in use
    course_count = skill.courses.count()
    job_count = skill.jobs_requiring.count()
    
    if request.method == 'POST':
        skill_name = skill.skill_name
        skill.delete()
        messages.success(request, f'Skill "{skill_name}" has been deleted.')
        return redirect('admin_skills')
    
    context = {
        'skill': skill,
        'course_count': course_count,
        'job_count': job_count,
    }
    return render(request, 'skillnest_app/admin_skill_delete.html', context)


@login_required(login_url='login')
def admin_contacts(request):
    """Contact message management"""
    from .models import ContactMessage
    
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    messages_list = ContactMessage.objects.all()
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'resolved':
        messages_list = messages_list.filter(is_resolved=True)
    elif status_filter == 'unresolved':
        messages_list = messages_list.filter(is_resolved=False)
    
    context = {
        'contact_messages': messages_list,
        'status_filter': status_filter,
    }
    return render(request, 'skillnest_app/admin_contacts.html', context)


@login_required(login_url='login')
def admin_resolve_contact(request, msg_id):
    """Mark a contact message as resolved"""
    from .models import ContactMessage
    
    # Check admin role
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
    contact_message = get_object_or_404(ContactMessage, pk=msg_id)
    
    if request.method == 'POST':
        contact_message.mark_resolved()
        messages.success(request, 'Message marked as resolved.')
    
    return redirect('admin_contacts')


# ==================== PORTFOLIO MANAGEMENT ====================
@login_required
def edit_profile(request):
    """Edit user profile"""
    profile = request.user.profile
    
    if request.method == 'POST':
        from .forms import UserProfileForm
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save()
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.email = form.cleaned_data.get('email', '')
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('portfolio', username=request.user.username)
    else:
        from .forms import UserProfileForm
        form = UserProfileForm(instance=profile)
    
    return render(request, 'skillnest_app/edit_profile.html', {'form': form})


# ==================== PORTFOLIO PROJECTS ====================
@login_required
def add_project(request):
    """Add a new portfolio project"""
    if request.method == 'POST':
        from .forms import PortfolioProjectForm
        form = PortfolioProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            form.save_m2m()
            messages.success(request, 'Project added successfully!')
            return redirect('portfolio', username=request.user.username)
    else:
        from .forms import PortfolioProjectForm
        form = PortfolioProjectForm()
    
    return render(request, 'skillnest_app/add_project.html', {'form': form})


@login_required
def edit_project(request, project_id):
    """Edit a portfolio project"""
    project = get_object_or_404(PortfolioProject, pk=project_id, user=request.user)
    
    if request.method == 'POST':
        from .forms import PortfolioProjectForm
        form = PortfolioProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('portfolio', username=request.user.username)
    else:
        from .forms import PortfolioProjectForm
        form = PortfolioProjectForm(instance=project)
    
    return render(request, 'skillnest_app/edit_project.html', {'form': form, 'project': project})


@login_required
def delete_project(request, project_id):
    """Delete a portfolio project"""
    project = get_object_or_404(PortfolioProject, pk=project_id, user=request.user)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('portfolio', username=request.user.username)
    
    return render(request, 'skillnest_app/delete_project.html', {'project': project})


# ==================== WORK EXPERIENCE ====================
@login_required
def add_work_experience(request):
    """Add work experience"""
    if request.method == 'POST':
        from .forms import WorkExperienceForm
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.user = request.user
            exp.save()
            form.save_m2m()
            messages.success(request, 'Work experience added successfully!')
            return redirect('portfolio', username=request.user.username)
    else:
        from .forms import WorkExperienceForm
        form = WorkExperienceForm()
    
    return render(request, 'skillnest_app/add_work_experience.html', {'form': form})


@login_required
def edit_work_experience(request, exp_id):
    """Edit work experience"""
    exp = get_object_or_404(WorkExperience, pk=exp_id, user=request.user)
    
    if request.method == 'POST':
        from .forms import WorkExperienceForm
        form = WorkExperienceForm(request.POST, instance=exp)
        if form.is_valid():
            form.save()
            messages.success(request, 'Work experience updated successfully!')
            return redirect('portfolio', username=request.user.username)
    else:
        from .forms import WorkExperienceForm
        form = WorkExperienceForm(instance=exp)
    
    return render(request, 'skillnest_app/edit_work_experience.html', {'form': form, 'experience': exp})


@login_required
def delete_work_experience(request, exp_id):
    """Delete work experience"""
    exp = get_object_or_404(WorkExperience, pk=exp_id, user=request.user)
    
    if request.method == 'POST':
        exp.delete()
        messages.success(request, 'Work experience deleted successfully!')
        return redirect('portfolio', username=request.user.username)
    
    return render(request, 'skillnest_app/delete_work_experience.html', {'experience': exp})


# ==================== EDUCATION ====================
@login_required
def add_education(request):
    """Add education"""
    if request.method == 'POST':
        from .forms import EducationForm
        form = EducationForm(request.POST)
        if form.is_valid():
            edu = form.save(commit=False)
            edu.user = request.user
            edu.save()
            messages.success(request, 'Education added successfully!')
            return redirect('portfolio', username=request.user.username)
    else:
        from .forms import EducationForm
        form = EducationForm()
    
    return render(request, 'skillnest_app/add_education.html', {'form': form})


@login_required
def edit_education(request, edu_id):
    """Edit education"""
    edu = get_object_or_404(Education, pk=edu_id, user=request.user)
    
    if request.method == 'POST':
        from .forms import EducationForm
        form = EducationForm(request.POST, instance=edu)
        if form.is_valid():
            form.save()
            messages.success(request, 'Education updated successfully!')
            return redirect('portfolio', username=request.user.username)
    else:
        from .forms import EducationForm
        form = EducationForm(instance=edu)
    
    return render(request, 'skillnest_app/edit_education.html', {'form': form, 'education': edu})


@login_required
def delete_education(request, edu_id):
    """Delete education"""
    edu = get_object_or_404(Education, pk=edu_id, user=request.user)
    
    if request.method == 'POST':
        edu.delete()
        messages.success(request, 'Education deleted successfully!')
        return redirect('portfolio', username=request.user.username)
    
    return render(request, 'skillnest_app/delete_education.html', {'education': edu})


# ==================== SOCIAL LINKS ====================
@login_required
def add_social_link(request):
    """Add social link"""
    if request.method == 'POST':
        from .forms import SocialLinkForm
        form = SocialLinkForm(request.POST, user=request.user)
        if form.is_valid():
            link = form.save(commit=False)
            link.user = request.user
            link.save()
            messages.success(request, 'Social link added successfully!')
            return redirect('portfolio', username=request.user.username)
    else:
        from .forms import SocialLinkForm
        form = SocialLinkForm(user=request.user)
    
    return render(request, 'skillnest_app/add_social_link.html', {'form': form})


@login_required
def edit_social_link(request, link_id):
    """Edit social link"""
    link = get_object_or_404(SocialLink, pk=link_id, user=request.user)
    
    if request.method == 'POST':
        from .forms import SocialLinkForm
        form = SocialLinkForm(request.POST, instance=link, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Social link updated successfully!')
            return redirect('portfolio', username=request.user.username)
    else:
        from .forms import SocialLinkForm
        form = SocialLinkForm(instance=link, user=request.user)
    
    return render(request, 'skillnest_app/edit_social_link.html', {'form': form, 'link': link})


@login_required
def delete_social_link(request, link_id):
    """Delete social link"""
    link = get_object_or_404(SocialLink, pk=link_id, user=request.user)
    
    if request.method == 'POST':
        link.delete()
        messages.success(request, 'Social link deleted successfully!')
        return redirect('portfolio', username=request.user.username)
    
    return render(request, 'skillnest_app/delete_social_link.html', {'link': link})
