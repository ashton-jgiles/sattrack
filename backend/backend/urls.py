# imports for the app urls to route to the correct urls.py file
from django.contrib import admin
from django.urls import path, include

# urls for routes
urlpatterns = [
    path('api/satellite/', include('satellites.urls')),
    path('api/dataset/', include('datasets.urls')),
    path('api/manage/satellite/', include('manage_satellites.urls')),
    path('api/manage/dataset/', include('manage_datasets.urls')),
    path('api/settings/', include('settings.urls')),
    path('api/lookups/', include('lookups.urls')),
    path('api/auth/', include('users.urls')),
    path('', include('frontend.urls')),
]
