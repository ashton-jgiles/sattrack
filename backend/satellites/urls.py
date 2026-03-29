from django.urls import path
from . import views

urlpatterns = [
    path('satellites/', views.SatelliteView.as_view()),
    path('<int:satellite_id>/', views.SpecificSatelliteView.as_view()),
    path('totalSatellites/', views.TotalSatellites.as_view()),
    path('totalEarthSatellites/', views.TotalEarthSatellites.as_view()),
    path('totalOceanicSatellites/', views.TotalOceanicSatellites.as_view()),
    path('totalNavigationSatellites/', views.TotalNavigationSatellites.as_view()),
    path('totalWeatherSatellites/', views.TotalWeatherSatellites.as_view()),
    path('totalInternetSatellites/', views.TotalInternetSatellites.as_view()),
    path('totalResearchSatellites/', views.TotalResearchSatellites.as_view()),
    path('positions/', views.AllTrajectory.as_view()),
    path('recentDeployments/', views.RecentDeployments.as_view()),
    path('<int:satellite_id>/profile/', views.SpecificSatelliteAllData.as_view()),
    path('<int:satellite_id>/delete/', views.DeleteSatellite.as_view()),
]