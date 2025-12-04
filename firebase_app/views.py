from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .firebase_listener import push_location

# Create your views here.
class PushLocationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            location_data = request.data.get("location_data")
            if not user_id or not location_data:
                return Response({"error": "user_id and location_data are required"}, status=status.HTTP_400_BAD_REQUEST)
            push_location(user_id, location_data)
            return Response({"message": "Location pushed successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
