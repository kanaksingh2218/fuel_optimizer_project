import os
from django.core.wsgi import get_wsgi_application

# Tell Django where your settings are
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# This is the "application" attribute the error was looking for
application = get_wsgi_application()