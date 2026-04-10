# path and views imports
from django.urls import path, re_path
from . import views

# get all frontend urls from the views as a regular expression so we dont need to add each route
urlpatterns = [
    re_path(r'^.*$', views.index),
]