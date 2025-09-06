from django.core.management.base import BaseCommand
from kafka import KafkaConsumer
import json
from app.models import RiderLocation  # replace with your model
from django.conf import settings

class Command(BaseCommand):
    help = 'Consume Kafka topic and insert into DB'

    def handle(self, *args, **kwargs):
        print("Starting Kafka consumer...")
        consumer = KafkaConsumer(
            'rider_locations',
            bootstrap_servers=settings.KAFKA_BROKER_URL,
            group_id='rider_locations_consumer',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
        )
        print("Kafka consumer started and listening to topic 'rider_locations'.")

        for message in consumer:
            print(f"Received message: {message.value}")
            data = message.value
            obj = RiderLocation.objects.create(**data)
            print(f"Inserted into DB: {obj}")
            self.stdout.write(self.style.SUCCESS(f"Inserted: {data}"))