"""
ASGI config for docker_django project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from docker_django.jwt_auth_middleware import JWTAuthMiddleware
import app.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docker_django.settings')

application = get_asgi_application()


application = ProtocolTypeRouter({
    "http": application,
     "websocket": JWTAuthMiddleware(
        URLRouter(
            app.routing.websocket_urlpatterns
        )
    ),
    # Just HTTP for now. (We can add other protocols later.)
})
