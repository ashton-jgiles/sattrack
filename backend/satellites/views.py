from django.shortcuts import render
from rest_framework import generics
from . import serializers
from . import models

class SatelliteView(generics.ListAPIView):
    queryset = models.Satellite.objects.all()
    serializer_class = serializers.SatelliteSerializer