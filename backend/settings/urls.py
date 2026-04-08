# path imports
from django.urls import path
from . import views

# settings app urls
urlpatterns = [
    path('trajectory/update/', views.UpdateTrajectories.as_view()),
]
