# path imports
from django.urls import path
from . import views

# dataset app urls
urlpatterns = [
    path('datasets/', views.DatasetView.as_view()),
    path('totalDatasets/', views.TotalDatasets.as_view()),
    path('<int:dataset_id>/satellites/', views.SatellitesInDataset.as_view()),
]