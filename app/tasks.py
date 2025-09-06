from celery import shared_task
import datetime

@shared_task
def test_celery(a, b):
    print("Celery is working!")
    return f"a + b = {a + b}, celery example"

# Sample periodic task for Celery Beat
@shared_task
def beat_sample_task():
    now = datetime.datetime.now()
    print(f"Celery Beat periodic task ran at {now}")
    return f"Beat ran at {now}"
