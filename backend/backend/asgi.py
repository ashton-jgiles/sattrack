# imports for creating our asgi application
import os
from django.core.asgi import get_asgi_application

# set the settings of the asgi application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# create the application
application = get_asgi_application()
