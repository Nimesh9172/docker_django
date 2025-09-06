from rest_framework import serializers
from .models import RiderLocation

class RiderLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiderLocation
        fields = ['rider_id', 'latitude', 'longitude', 'timestamp']


        