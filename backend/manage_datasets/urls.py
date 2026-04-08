# path and views imports
from django.urls import path
from . import views

# manage datasets app urls
urlpatterns = [
    path('<int:dataset_id>/modify/', views.ModifyDataset.as_view()),
    path('<int:dataset_id>/delete/', views.DeleteDataset.as_view()),
    path('<int:dataset_id>/review/', views.ReviewDataset.as_view()),
    path('add/', views.AddDataset.as_view()),
    path('sources/', views.DatasetSources.as_view()),
    path('reviews/', views.GetReviewDatasets.as_view()),
]
