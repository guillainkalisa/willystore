import os
import django
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "willystore.settings")
django.setup()

from django.contrib.auth.models import User
django.setup()

# Create a test superuser if not exists
user, created = User.objects.get_or_create(username='testadmin', is_superuser=True, is_staff=True)
if created:
    user.set_password('testpassword')
    user.save()

client = Client()
client.login(username='testadmin', password='testpassword')

response = client.get('/dashboard/', HTTP_HOST='127.0.0.1')
print(f"Status Code: {response.status_code}")
if response.status_code != 200:
    content = response.content.decode('utf-8')
    import re
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    if title_match:
        print(f"Error Title: {title_match.group(1)}")
    else:
        print("No title found in error response.")
    
    # Try to find exception value
    exc_match = re.search(r'<pre class="exception_value">(.*?)</pre>', content, re.IGNORECASE | re.DOTALL)
    if exc_match:
        print(f"Exception Value: {exc_match.group(1).strip()}")
else:
    print("Success: Dashboard returned 200 OK")
