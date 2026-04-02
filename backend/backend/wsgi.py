# imports for creating the wsgi application
import os
from django.core.wsgi import get_wsgi_application

# set the settings on the os to the backend settings file
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# create the application
application = get_wsgi_application()
