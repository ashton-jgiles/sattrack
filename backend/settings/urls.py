# path imports
from django.urls import path
from . import views

# lookups app urls
urlpatterns = [
    path('trajectory/update/', views.UpdateTrajectories.as_view()),
]