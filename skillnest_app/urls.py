from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Home & General
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Courses
    path('courses/', views.courses, name='courses'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/lesson/<int:lesson_id>/', views.watch_lesson, name='watch_lesson'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('lessons/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    
    # Certificates
    path('certificate/<int:certificate_id>/', views.certificate_view, name='certificate_view'),
    
    # Portfolio
    path('portfolio/<str:username>/', views.portfolio, name='portfolio'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Portfolio Projects
    path('project/add/', views.add_project, name='add_project'),
    path('project/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    
    # Work Experience
    path('experience/add/', views.add_work_experience, name='add_work_experience'),
    path('experience/<int:exp_id>/edit/', views.edit_work_experience, name='edit_work_experience'),
    path('experience/<int:exp_id>/delete/', views.delete_work_experience, name='delete_work_experience'),
    
    # Education
    path('education/add/', views.add_education, name='add_education'),
    path('education/<int:edu_id>/edit/', views.edit_education, name='edit_education'),
    path('education/<int:edu_id>/delete/', views.delete_education, name='delete_education'),
    
    # Social Links
    path('social-link/add/', views.add_social_link, name='add_social_link'),
    path('social-link/<int:link_id>/edit/', views.edit_social_link, name='edit_social_link'),
    path('social-link/<int:link_id>/delete/', views.delete_social_link, name='delete_social_link'),
    
    # Jobs & Recommendations
    path('jobs/', views.jobs, name='jobs'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('recommended-jobs/', views.recommended_jobs, name='recommended_jobs'),
    
    # Skills
    path('skill-gap/', views.skill_gap, name='skill_gap'),
    
    # Teachers
    path('teachers/', views.teachers, name='teachers'),
    path('teachers/<str:username>/', views.teacher_profile, name='teacher_profile'),
]

# teacher create route
urlpatterns += [
    path('teacher/course/add/', views.teacher_create_course, name='teacher_create_course'),
    path('teacher/course/<int:course_id>/edit/', views.teacher_edit_course, name='teacher_edit_course'),
    path('teacher/course/<int:course_id>/delete/', views.teacher_delete_course, name='teacher_delete_course'),
    path('teacher/course/<int:course_id>/students/', views.teacher_course_students, name='teacher_course_students'),
    path('teacher/course/<int:course_id>/lesson/add/', views.teacher_add_lesson, name='teacher_add_lesson'),
    path('teacher/lesson/<int:lesson_id>/edit/', views.teacher_edit_lesson, name='teacher_edit_lesson'),
    path('teacher/lesson/<int:lesson_id>/delete/', views.teacher_delete_lesson, name='teacher_delete_lesson'),
    path('teacher/course/management/', views.teacher_course_management, name='teacher_course_management'),
]

# Admin Panel Routes
urlpatterns += [
    # Admin Dashboard
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    
    # User Management
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/<int:user_id>/toggle-status/', views.admin_toggle_user_status, name='admin_toggle_user_status'),
    path('admin-panel/users/<int:user_id>/approve-teacher/', views.admin_approve_teacher, name='admin_approve_teacher'),
    
    # Course Management
    path('admin-panel/courses/', views.admin_courses, name='admin_courses'),
    path('admin-panel/courses/<int:course_id>/delete/', views.admin_delete_course, name='admin_delete_course'),
    
    # Certificate Management
    path('admin-panel/certificates/', views.admin_certificates, name='admin_certificates'),
    path('admin-panel/certificates/<int:cert_id>/revoke/', views.admin_revoke_certificate, name='admin_revoke_certificate'),
    
    # Job Management
    path('admin-panel/jobs/', views.admin_jobs, name='admin_jobs'),
    path('admin-panel/jobs/create/', views.admin_create_job, name='admin_create_job'),
    path('admin-panel/jobs/<int:job_id>/edit/', views.admin_edit_job, name='admin_edit_job'),
    path('admin-panel/jobs/<int:job_id>/delete/', views.admin_delete_job, name='admin_delete_job'),
    path('admin-panel/jobs/<int:job_id>/toggle-status/', views.admin_toggle_job_status, name='admin_toggle_job_status'),
    
    # Skill Management
    path('admin-panel/skills/', views.admin_skills, name='admin_skills'),
    path('admin-panel/skills/create/', views.admin_create_skill, name='admin_create_skill'),
    path('admin-panel/skills/<int:skill_id>/edit/', views.admin_edit_skill, name='admin_edit_skill'),
    path('admin-panel/skills/<int:skill_id>/delete/', views.admin_delete_skill, name='admin_delete_skill'),
    
    # Contact Management
    path('admin-panel/contacts/', views.admin_contacts, name='admin_contacts'),
    path('admin-panel/contacts/<int:msg_id>/resolve/', views.admin_resolve_contact, name='admin_resolve_contact'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
