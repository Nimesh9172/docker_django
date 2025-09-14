from django.urls import re_path
from . import consumer

websocket_urlpatterns = [
    re_path(r"ws/echo/$", consumer.EchoConsumer.as_asgi()),
    re_path(r"ws/rider/(?P<rider_id>\w+)/$", consumer.RiderLocationConsumer.as_asgi()),
]
