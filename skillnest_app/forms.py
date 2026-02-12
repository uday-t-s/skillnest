from django import forms
from django.forms.widgets import ClearableFileInput
from .models import Course, Skill, Lesson, Job, SocialLink, UserProfile, PortfolioProject, WorkExperience, Education


class CourseCreateForm(forms.ModelForm):
	# Optional initial lesson fields (not part of Course model)
	initial_lesson_title = forms.CharField(required=False, max_length=200, label='First Lesson Title')
	initial_lesson_video_file = forms.FileField(required=False, label='First Lesson Video File', widget=ClearableFileInput)
	initial_lesson_video_url = forms.URLField(required=False, label='First Lesson Video Embed URL')

	class Meta:
		model = Course
		fields = ['title', 'description', 'category', 'level', 'cover_image', 'duration_hours', 'skills']
		widgets = {
			'skills': forms.CheckboxSelectMultiple,
		}


class LessonForm(forms.ModelForm):
	class Meta:
		model = Lesson
		fields = ['title', 'description', 'order', 'video_url', 'video_file', 'content', 'duration_minutes']
		widgets = {
			'video_file': ClearableFileInput,
		}


# ==================== ADMIN FORMS ====================

class JobForm(forms.ModelForm):
	"""Form for creating and editing job postings"""
	class Meta:
		model = Job
		fields = [
			'job_title', 'company_name', 'location', 'description', 
			'salary_min', 'salary_max', 'job_type', 'requirements',
			'skills_required', 'last_date', 'is_active'
		]
		widgets = {
			'description': forms.Textarea(attrs={'rows': 5}),
			'requirements': forms.Textarea(attrs={'rows': 4}),
			'skills_required': forms.CheckboxSelectMultiple(),
			'last_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
		}


class SkillForm(forms.ModelForm):
	"""Form for creating and editing skills"""
	class Meta:
		model = Skill
		fields = ['skill_name', 'description', 'category']
		widgets = {
			'description': forms.Textarea(attrs={'rows': 3}),
		}


class SocialLinkForm(forms.ModelForm):
	"""Form for adding and editing social links"""
	class Meta:
		model = SocialLink
		fields = ['platform', 'url', 'display_name']
		widgets = {
			'url': forms.URLInput(attrs={'placeholder': 'https://example.com'}),
			'display_name': forms.TextInput(attrs={'placeholder': 'Optional display name'}),
		}

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super().__init__(*args, **kwargs)

	def clean(self):
		cleaned_data = super().clean()
		platform = cleaned_data.get('platform')
		if self.user and platform:
			queryset = SocialLink.objects.filter(user=self.user, platform=platform)
			if self.instance:
				queryset = queryset.exclude(pk=self.instance.pk)
			if queryset.exists():
				raise forms.ValidationError(f"You already have a social link for {dict(SocialLink.PLATFORM_CHOICES)[platform]}.")
		return cleaned_data


class UserProfileForm(forms.ModelForm):
	"""Form for editing user profile"""
	class Meta:
		model = UserProfile
		fields = ['bio', 'profile_picture', 'phone', 'specialization', 'expertise', 'experience_years', 'linkedin_url', 'website_url']
		widgets = {
			'bio': forms.Textarea(attrs={'rows': 4}),
			'expertise': forms.Textarea(attrs={'rows': 3}),
			'profile_picture': ClearableFileInput(),
		}


class PortfolioProjectForm(forms.ModelForm):
	"""Form for adding and editing portfolio projects"""
	class Meta:
		model = PortfolioProject
		fields = ['title', 'description', 'short_description', 'technologies', 'image', 'live_url', 'github_url']
		widgets = {
			'description': forms.Textarea(attrs={'rows': 5}),
			'short_description': forms.Textarea(attrs={'rows': 2}),
			'technologies': forms.CheckboxSelectMultiple(),
			'image': ClearableFileInput(),
		}


class WorkExperienceForm(forms.ModelForm):
	"""Form for adding and editing work experience"""
	class Meta:
		model = WorkExperience
		fields = ['company_name', 'job_title', 'description', 'start_date', 'end_date', 'is_current', 'skills_used']
		widgets = {
			'description': forms.Textarea(attrs={'rows': 4}),
			'start_date': forms.DateInput(attrs={'type': 'date'}),
			'end_date': forms.DateInput(attrs={'type': 'date'}),
			'skills_used': forms.CheckboxSelectMultiple(),
		}


class EducationForm(forms.ModelForm):
	"""Form for adding and editing education"""
	class Meta:
		model = Education
		fields = ['school_name', 'degree', 'field_of_study', 'start_date', 'end_date', 'is_current', 'grade', 'activities']
		widgets = {
			'start_date': forms.DateInput(attrs={'type': 'date'}),
			'end_date': forms.DateInput(attrs={'type': 'date'}),
			'activities': forms.Textarea(attrs={'rows': 3}),
		}
