import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skillnest.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from skillnest_app.models import Certificate

User = get_user_model()
client = Client()
client.defaults['HTTP_HOST'] = '127.0.0.1'

cert = Certificate.objects.first()
if not cert:
    print('No certificate found')
    sys.exit(0)

cert_url = f"/certificate/{cert.id}/"
print('Testing URL:', cert_url)

# Anonymous request
resp_anonymous = client.get(cert_url)
print('Anonymous status:', resp_anonymous.status_code)
print('Anonymous redirected to:', resp_anonymous.url if resp_anonymous.status_code in (301,302) else 'no redirect')

# Force login as certificate owner
client.force_login(cert.user)
resp_owner = client.get(cert_url)
print('Owner status:', resp_owner.status_code)
print('Owner content length:', len(resp_owner.content))
