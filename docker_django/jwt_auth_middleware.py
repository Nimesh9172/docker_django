from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from docker_django.redis_client import r  # Import the Redis client

User = get_user_model()


@database_sync_to_async
def get_user(validated_token):
    try:
        jwt_auth = JWTAuthentication()
        user = jwt_auth.get_user(validated_token)
        return user
    except Exception:
        return None

@database_sync_to_async
def get_user_from_redis(ws_token: str):
    """Check if Redis token exists and return user"""
    user_id = r.get(f"ws:{ws_token}")
    if user_id:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    return None


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        token = None

        # 1. Subprotocols
        subprotocols = scope.get("subprotocols", [])
        if subprotocols:
            if len(subprotocols) >= 2 and subprotocols[0].lower() in ["jwt", "token"]:
                token = subprotocols[1]
            elif len(subprotocols) == 1:
                value = subprotocols[0]
                parts = value.split(" ", 1)
                if len(parts) == 2 and parts[0].lower() in ["jwt", "token"]:
                    token = parts[1]
                else:
                    token = value

        # 2. Query string
        if not token:
            query_string = scope.get("query_string", b"").decode()
            query_params = parse_qs(query_string)
            token_list = query_params.get("token") or query_params.get("jwt")
            if token_list:
                token = token_list[0]

        print("Subprotocols:", subprotocols, "Extracted token:", token)

        # --- Validate ---
        if token:
            user = None
            try:
                # Try JWT first
                validated_token = UntypedToken(token)
                if not validated_token.payload.get("ws"):
                    raise InvalidToken("HTTP tokens are no longer valid for WebSocket auth.")
                user = await get_user(validated_token)
            except Exception:
                # Try Redis WS token
                user = await get_user_from_redis(token)

            scope["user"] = user if user else AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
    