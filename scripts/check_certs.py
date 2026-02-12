import os
import sys
import django

# Ensure project root is on sys.path so Django project imports work
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skillnest.settings')
django.setup()

from skillnest_app.models import Certificate

print('Certificate count:', Certificate.objects.count())
for c in Certificate.objects.all()[:10]:
    print(f'id={c.id} code={c.certificate_code} user={c.user.username} course={c.course.title}')
