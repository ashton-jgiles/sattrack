from django.urls import path
from . import views

urlpatterns = [
    path('satellite/<int:satellite_id>/delete/', views.DeleteSatellite.as_view()),
    path('satellite/modify/', views.ModifySatellite.as_view()),
    path('satellite/dataset/<int:dataset_id>/new/', views.NewSatellitesFromDataset.as_view()),
]