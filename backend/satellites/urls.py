from django.urls import path
from . import views

urlpatterns = [
    path('satellites/', views.SatelliteView.as_view()),
    path('<int:satellite_id>/', views.SpecificSatelliteView.as_view())
]