from django.urls import path
from . import views

urlpatterns = [
    path('datasets/', views.DatasetView.as_view()),
    path('totalDatasets/', views.TotalDatasets.as_view()),
]