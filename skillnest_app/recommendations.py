"""
Job Recommendation Engine
Simple rule-based algorithm to match student skills with job requirements.
This is the "AI-powered" recommendation logic.
"""

from .models import Job, StudentSkill, JobRecommendation, Skill
from django.db.models import Count, Prefetch


def calculate_match_score(user_skill_ids, job_skill_ids):
    """
    Calculate match score between student skills and job requirements.
    
    Score = (matched_skills_count / total_required_skills) * 100
    
    Args:
        user_skill_ids: List of skill IDs the student has
        job_skill_ids: List of skill IDs required for the job
    
    Returns:
        Tuple: (match_score: float, matched_count: int, required_count: int)
    """
    user_skills_set = set(user_skill_ids)
    job_skills_set = set(job_skill_ids)
    
    if not job_skills_set:
        return 0.0, 0, 0
    
    matched_skills = len(user_skills_set & job_skills_set)
    total_required = len(job_skills_set)
    
    match_score = (matched_skills / total_required) if total_required > 0 else 0.0
    
    return match_score, matched_skills, total_required


def get_job_recommendations(user, user_skill_ids, limit=10):
    """
    Get recommended jobs for a user based on their skills.
    
    Algorithm:
    1. Get all active jobs
    2. For each job, calculate match score
    3. Filter jobs with match score > 0 (at least one skill matches)
    4. Sort by match score descending
    5. Return top recommendations with detailed info
    
    Args:
        user: User object
        user_skill_ids: List of skill IDs the user has
        limit: Maximum number of recommendations to return
    
    Returns:
        List of job objects with match_score, matched_skills_count, etc.
    """
    
    # Get all active jobs
    active_jobs = Job.objects.filter(is_active=True).prefetch_related('skills_required')
    
    recommendations = []
    
    for job in active_jobs:
        job_skill_ids = list(job.skills_required.values_list('id', flat=True))
        
        match_score, matched_count, required_count = calculate_match_score(
            user_skill_ids, job_skill_ids
        )
        
        # Only include jobs with at least one matching skill (>0% match)
        if match_score > 0:
            # Create a recommendation object with detailed info
            rec_data = {
                'job': job,
                'match_score': match_score,
                'match_percent': int(match_score * 100),
                'matched_skills_count': matched_count,
                'total_required_skills': required_count,
                'missing_skills_count': required_count - matched_count,
            }
            
            # Get the missing skills for display
            user_skills_set = set(user_skill_ids)
            job_skills_set = set(job_skill_ids)
            missing_skill_ids = job_skills_set - user_skills_set
            
            if missing_skill_ids:
                rec_data['missing_skills'] = Skill.objects.filter(id__in=missing_skill_ids)
            else:
                rec_data['missing_skills'] = []
            
            recommendations.append(rec_data)
    
    # Sort by match score (descending), then by posted date (newer first)
    recommendations.sort(key=lambda x: (-x['match_score'], -x['job'].posted_date.timestamp()))
    
    # Return top recommendations
    return recommendations[:limit]


def generate_recommendations_for_user(user):
    """
    Generate and store recommendations in the database for a user.
    This can be called after a student completes a course and gains a skill.
    
    Args:
        user: User object
    """
    # Get user's current skills
    user_skill_ids = list(StudentSkill.objects.filter(user=user).values_list('skill_id', flat=True))
    
    if not user_skill_ids:
        return []
    
    # Get recommendations
    recs = get_job_recommendations(user, user_skill_ids, limit=50)
    
    # Store in database for quick retrieval
    stored_recs = []
    for rec in recs:
        job_rec, created = JobRecommendation.objects.update_or_create(
            user=user,
            job=rec['job'],
            defaults={
                'match_score': rec['match_score'],
                'matched_skills_count': rec['matched_skills_count'],
                'total_required_skills': rec['total_required_skills'],
            }
        )
        stored_recs.append(job_rec)
    
    return stored_recs


def get_skill_gap_analysis(user, career_path):
    """
    Analyze skill gap for a user relative to a career path.
    
    Args:
        user: User object
        career_path: CareerPath object
    
    Returns:
        Dict with career_name, required_skills, user_skills, missing_skills, completion_percent
    """
    user_skill_ids = set(
        StudentSkill.objects.filter(user=user).values_list('skill_id', flat=True)
    )
    
    required_skill_ids = set(
        career_path.required_skills.values_list('id', flat=True)
    )
    
    missing_skill_ids = required_skill_ids - user_skill_ids
    
    if required_skill_ids:
        completion_percent = ((len(required_skill_ids) - len(missing_skill_ids)) / len(required_skill_ids)) * 100
    else:
        completion_percent = 100
    
    return {
        'career': career_path,
        'required_skills': career_path.required_skills.all(),
        'user_skills': StudentSkill.objects.filter(user=user, skill__in=career_path.required_skills.all()),
        'missing_skills': career_path.required_skills.filter(id__in=missing_skill_ids),
        'completion_percent': int(completion_percent),
        'total_required': len(required_skill_ids),
        'skills_acquired': len(required_skill_ids) - len(missing_skill_ids),
    }
