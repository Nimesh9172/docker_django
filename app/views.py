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
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from datetime import timedelta
from rest_framework import permissions
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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
    

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")

            user = authenticate(username=username, password=password)
            if user is None:    
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)
            data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class RiderLocationAddUpdateView(APIView):
    permission_classes = [permissions.AllowAny]
    authication_classes = []

    def post(self, request):
        try:
            obj, created = RiderLocation.objects.update_or_create(
                rider_id=request.data.get("rider_id"),
                defaults={
                    "latitude": request.data.get("latitude"),
                    "longitude": request.data.get("longitude"),
                }
            )

            serializer = RiderLocationSerializer(obj)
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"rider_{obj.rider_id}_updates",
                    {
                        "type": "rider_update",
                        "data": serializer.data,
                    },
                )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GenerateWSTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        ws_token = AccessToken.for_user(user)
        ws_token["ws"] = True   # custom claim to mark WS tokens
        ws_token.set_exp(lifetime=timedelta(minutes=5)) 
        return Response({"ws_token": str(ws_token)})



from docker_django.redis_client import r
import uuid


def generate_ws_key(user_id, ttl=300):
    key = str(uuid.uuid4())
    r.setex(f"ws:{key}", ttl, user_id)
    return key

class GenerateWSRedisTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            ws_key = generate_ws_key(request.user.id, ttl=300)  # 5 min TTL
            return Response({"ws_key": ws_key})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
