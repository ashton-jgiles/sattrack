from django.urls import path
from . import views

urlpatterns = [
    path('<int:dataset_id>/modify/', views.ModifyDataset.as_view()),
    path('<int:dataset_id>/delete/', views.DeleteDataset.as_view()),
    path('add/', views.AddDataset.as_view()),
    path('sources/', views.DatasetSources.as_view()),
]
