import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skillnest.settings')
import django
django.setup()

from django.test import Client
from skillnest_app.models import Certificate

client = Client()
client.defaults['HTTP_HOST'] = '127.0.0.1'

cert = Certificate.objects.first()
cert_url = f"/certificate/{cert.id}/"

# Force login as owner
client.force_login(cert.user)
resp = client.get(cert_url)

if resp.status_code == 200:
    content = resp.content.decode('utf-8')
    # Check key elements
    checks = [
        ('Certificate title', 'Certificate of Completion' in content),
        ('Student name', cert.user.username in content or (cert.user.first_name and cert.user.last_name and f"{cert.user.first_name} {cert.user.last_name}" in content)),
        ('Course name', cert.course.title in content),
        ('Certificate ID', cert.certificate_code in content),
        ('Download button', 'Download PDF' in content or 'downloadPDF' in content),
    ]
    
    print(f'Certificate ID {cert.id} - Status: {resp.status_code}\n')
    for check_name, result in checks:
        print(f"  {'✓' if result else '✗'} {check_name}")
else:
    print(f'Error: {resp.status_code}')
