import os
import json
import base64
from django.apps import AppConfig
from django.conf import settings
import threading
import logging
from firebase_admin import initialize_app, credentials

IS_FIREBASE_ENABLED = settings.IS_FIREBASE_ENABLED

logger = logging.getLogger(__name__)



# Private variable for singleton Firebase app
_firebase_app = None
_firebase_lock = threading.Lock()

def get_firebase_app():
    """Get the initialized Firebase app instance."""
    global _firebase_app
    return _firebase_app

def init_firebase():
    """Initialize Firebase in a background thread."""
    global _firebase_app
    try:
        credentials_b64 = os.environ.get("FIREBASE_CREDENTIAL_JSON")
        if not credentials_b64:
            logger.warning("FIREBASE_CREDENTIAL_JSON not found in environment")
            return
        credentials_bytes = base64.b64decode(credentials_b64)
        credentials_str = credentials_bytes.decode('utf-8')
        credentials_json = json.loads(credentials_str)
        cred = credentials.Certificate(credentials_json)

        with _firebase_lock:
            if _firebase_app is None:
                _firebase_app = initialize_app(cred, {
                    'databaseURL': settings.FIREBASE_DB_URL
                })
                logger.info("Firebase initialized successfully with firebase db url")
            else:
                logger.info("Firebase app already initialized")
    except Exception as e:
        logger.error(f"Firebase initialization failed: {e}", exc_info=True)



class FirebaseAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'firebase_app'

    def ready(self):
        if IS_FIREBASE_ENABLED:
            threading.Thread(target=init_firebase, daemon=True).start()

            # Start listener after Firebase initializes
            def delayed_listener_start():
                import time
                time.sleep(2)
                from .firebase_listener import start_listener
                start_listener()  # Listen to all notifications

            threading.Thread(target=delayed_listener_start, daemon=True).start()