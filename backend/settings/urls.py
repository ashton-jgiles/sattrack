# path and views imports
from django.urls import path
from . import views

# settings app urls
urlpatterns = [
    path('trajectory/update/', views.UpdateTrajectories.as_view()),
    path('trajectory/status/', views.TrajectoryStatus.as_view()),
]
