from django.urls import path
from . import views

urlpatterns = [
    path('push/', views.PushLocationView.as_view(), name='push-location'),
]
