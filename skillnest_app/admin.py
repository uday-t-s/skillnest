from django.contrib import admin
from .models import (
    UserProfile, Skill, Course, Lesson, Enrollment, StudentSkill,
    Certificate, Job, JobRecommendation, CareerPath
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('skill_name', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('skill_name', 'description')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'level', 'instructor', 'duration_hours', 'created_at')
    list_filter = ('category', 'level', 'created_at')
    search_fields = ('title', 'description', 'instructor__username')
    filter_horizontal = ('skills',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'duration_minutes', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'course__title')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status', 'progress_percent', 'enroll_date')
    list_filter = ('status', 'enroll_date', 'course__category')
    search_fields = ('user__username', 'course__title')


@admin.register(StudentSkill)
class StudentSkillAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'proficiency_level', 'acquired_date')
    list_filter = ('proficiency_level', 'acquired_date')
    search_fields = ('user__username', 'skill__skill_name')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'certificate_code', 'issue_date')
    list_filter = ('issue_date',)
    search_fields = ('user__username', 'course__title', 'certificate_code')
    readonly_fields = ('issue_date',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'company_name', 'location', 'job_type', 'posted_date', 'is_active')
    list_filter = ('job_type', 'is_active', 'posted_date')
    search_fields = ('job_title', 'company_name', 'location')
    filter_horizontal = ('skills_required',)


@admin.register(JobRecommendation)
class JobRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'match_score', 'matched_skills_count', 'total_required_skills')
    list_filter = ('recommended_at', 'match_score')
    search_fields = ('user__username', 'job__job_title')
    readonly_fields = ('recommended_at',)


@admin.register(CareerPath)
class CareerPathAdmin(admin.ModelAdmin):
    list_display = ('career_name', 'experience_level', 'created_at')
    list_filter = ('experience_level', 'created_at')
    search_fields = ('career_name', 'description')
    filter_horizontal = ('required_skills',)
