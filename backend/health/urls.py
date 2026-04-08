# path and views imports
from django.urls import path
from . import views

# health app urls
urlpatterns = [
    path('', views.HealthCheck.as_view()),
]
