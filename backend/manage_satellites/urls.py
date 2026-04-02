# path imports
from django.urls import path
from . import views

# manage satellite app urls
urlpatterns = [
    path('<int:satellite_id>/delete/', views.DeleteSatellite.as_view()),
    path('modify/', views.ModifySatellite.as_view()),
    path('dataset/<int:dataset_id>/new/', views.NewSatellitesFromDataset.as_view()),
    path('create/', views.CreateSatellite.as_view()),
]