from django.urls import path
from . import views

urlpatterns = [
    path('totalDatasets/', views.TotalDatasets.as_view()),
]