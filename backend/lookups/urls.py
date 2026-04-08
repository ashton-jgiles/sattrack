# path and views imports
from django.urls import path
from . import views

# lookups app urls
urlpatterns = [
    path('owners/',   views.AllOwners.as_view()),
    path('vehicles/', views.AllVehicles.as_view()),
    path('sites/',    views.AllLaunchSites.as_view()),
    path('stations/', views.AllCommunicationStations.as_view()),
]
