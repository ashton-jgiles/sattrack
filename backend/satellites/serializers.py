from rest_framework import serializers
from . import models

class SatelliteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Satellite
        fields = '__all__'