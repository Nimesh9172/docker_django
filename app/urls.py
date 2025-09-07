from django.urls import path
from .views import RiderLocationListView, RiderLocationUpdateView, health_check, trigger_celery_task

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('trigger-task/', trigger_celery_task, name='trigger_celery_task'),
    path('rider/location/', RiderLocationUpdateView.as_view(), name='rider-location'),
    path('rider/locations/', RiderLocationListView.as_view(), name='rider-locations'),
]
