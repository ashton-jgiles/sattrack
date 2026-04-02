# path imports
from django.urls import path
from . import views

# users app urls
urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('register/', views.CreateAccountView.as_view()),
]