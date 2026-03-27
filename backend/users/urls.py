from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('register/', views.CreateAccountView.as_view()),
]