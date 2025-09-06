from django.shortcuts import render

# Create your views here.
from app.models import RiderLocation
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tasks import test_celery


@api_view(['GET'])
def health_check(request):
	return Response({"status": "ok"}, status=200)

@api_view(['GET'])
def trigger_celery_task(request):
	result = test_celery.apply_async(args=[1, 2])
	return Response({"task_id": result.id, "status": "Task triggered"}, status=200)

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import RiderLocationSerializer
from django.conf import settings
from kafka import KafkaProducer
import json

class RiderLocationUpdateView(APIView):
    def post(self, request):
        serializer = RiderLocationSerializer(data=request.data)
        if serializer.is_valid():
            # Save to DB
            # location = serializer.save()
            # Produce to Kafka
            producer = KafkaProducer(
                bootstrap_servers=[settings.KAFKA_BROKER_URL],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            producer.send('rider_locations', serializer.data, partition=0)  # Send to partition 1
            producer.flush()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RiderLocationListView(APIView):
    def get(self, request):
            locations = RiderLocation.objects.all().order_by('-timestamp')[:100]  # Get last 100 locations
            serializer = RiderLocationSerializer(locations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)