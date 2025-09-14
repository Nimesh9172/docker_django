from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('trigger-task/', views.trigger_celery_task, name='trigger_celery_task'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('rider/location/', views.RiderLocationUpdateView.as_view(), name='rider-location'),
    path('rider/locations/', views.RiderLocationListView.as_view(), name='rider-locations'),
    path('update-location/', views.RiderLocationAddUpdateView.as_view(), name='update-location'),
    path('ws-token/', views.GenerateWSTokenView.as_view(), name='ws-token'),
    path('ws-redis-token/', views.GenerateWSRedisTokenView.as_view(), name='ws-redis-token'),
]
