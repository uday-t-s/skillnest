from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


def teacher_required(view_func):
    """Decorator that ensures the user is logged in and is a teacher.

    - Redirects to `login` if the user is not authenticated.
    - Redirects to `dashboard` if the user is authenticated but not a teacher.
    """
    @login_required(login_url='login')
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = request.user
        # Ensure profile exists and has role 'teacher'
        if not hasattr(user, 'profile') or getattr(user.profile, 'role', None) != 'teacher':
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)

    return _wrapped


def admin_required(view_func):
    """Decorator that ensures the user is logged in and is an admin.

    - Redirects to `login` if the user is not authenticated.
    - Redirects to `dashboard` if the user is authenticated but not an admin.
    """
    @login_required(login_url='login')
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = request.user
        # Ensure profile exists and has role 'admin'
        if not hasattr(user, 'profile') or getattr(user.profile, 'role', None) != 'admin':
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)

    return _wrapped
