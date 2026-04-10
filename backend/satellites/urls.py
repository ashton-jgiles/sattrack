# path and views imports
from django.urls import path
from . import views

# satellite app urls
urlpatterns = [
    path('satellites/', views.SatelliteView.as_view()),
    path('<int:satellite_id>/', views.SpecificSatelliteView.as_view()),
    path('counts/', views.SatelliteTypeCounts.as_view()),
    path('positions/', views.AllTrajectory.as_view()),
    path('recent_deployments/', views.RecentDeployments.as_view()),
    path('<int:satellite_id>/profile/', views.SpecificSatelliteAllData.as_view()),
]
