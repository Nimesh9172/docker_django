import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docker_django.settings')

app = Celery('docker_django')

# Load celery config from Django settings, using CELERY_ namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# ✅ Celery Beat schedule for testing
app.conf.beat_schedule = {
    'beat-sample-task-every-minute': {
        'task': 'app.tasks.beat_sample_task',
        'schedule': crontab(minute='*/1'),  # every 1 minute
    },
}

# Optional: timezone for beat (otherwise defaults to UTC)
app.conf.timezone = 'UTC'
