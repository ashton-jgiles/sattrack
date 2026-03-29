from django.urls import path
from . import views

urlpatterns = [
    path('lookup/owners/',   views.AllOwners.as_view()),
    path('lookup/vehicles/', views.AllVehicles.as_view()),
    path('lookup/sites/',    views.AllLaunchSites.as_view()),
    path('lookup/stations/', views.AllCommunicationStations.as_view()),
]