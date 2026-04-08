# path imports
from django.urls import path
from . import views

# users app urls
urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('register/', views.CreateAccountView.as_view()),
    path('users/', views.GetUsers.as_view()),
    path('<str:username>/userProfile/', views.GetUserProfile.as_view()),
    path('user/modify/', views.ModifyUser.as_view()),
    path('user/<str:username>/delete/', views.DeleteUser.as_view()),
    path('me/update/', views.UpdateOwnProfile.as_view()),
    path('me/password/', views.ChangePassword.as_view()),
]
