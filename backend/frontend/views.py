# import render
from django.shortcuts import render

# index view which takes the request args and kwargs and calls render on the index.html to create our react frontend
def index(request, *args, **kwargs):
    return render(request, 'frontend/index.html')
