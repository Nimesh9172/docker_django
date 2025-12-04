import logging
from firebase_admin import db
from .apps import get_firebase_app

logger = logging.getLogger(__name__)


def start_listener(user_id=None):
    """
    Start listening to notification changes.
    
    Args:
        user_id: If provided, listen only to this user's location.
                 If None, listen to all locations.
    """
    app = get_firebase_app()
    if not app:
        logger.warning("Firebase app not initialized, cannot start listener")
        return None
    
    try:
        path = f'jobs/{user_id}' if user_id else 'jobs'
        ref = db.reference(path, app=app)
        ref.listen(on_location_change)
        logger.info(f"Listener started for path: {path}")
        return ref
    except Exception as e:
        logger.error(f"Failed to start listener: {e}", exc_info=True)
        return None

def push_location(user_id, location_data):
    """
    Push a new location update to Realtime Database.
    Creates a unique ID automatically.
    
    Args:
        user_id: User ID to send location update to
        location_data: Dict with location details
    
    Returns:
        The unique key of the created notification
    """
    app = get_firebase_app()
    if not app:
        logger.error("Firebase app not initialized")
        return None
    
    try:
        # Reference to user's notifications
        ref = db.reference(f'jobs', app=app)

        # Push creates a new child with unique ID
        new_ref = ref.push(location_data)

        logger.info(f"Location update pushed: {new_ref.key}")
        return new_ref.key
    except Exception as e:
        logger.error(f"Failed to push location update: {e}", exc_info=True)
        return None

def on_location_change(event):
    """
    Callback when location data changes.

    Event types:
    - 'put': Data was added or completely replaced
    - 'patch': Partial update to data
    - 'keep-alive': Connection is alive
    - 'cancel': Listener was cancelled
    - 'auth_revoked': Authentication was revoked
    """
    logger.info(f"Location event: {event.event_type}")
    logger.info(f"Path: {event.path}")
    # logger.info(f"Data: {event.data}")
    
    if event.event_type == 'put':
        # Handle new or updated location
        handle_location_update(event.path, event.data)
    elif event.event_type == 'patch':
        # Handle partial update
        logger.info(f"Partial update at {event.path}")

def handle_location_update(path, data):
    """
    Process location updates.
    You can update Django models, send webhooks, etc.
    """
    logger.info(f"Processing location update: {path}")
    logger.info(f"Processing location data: {data}")