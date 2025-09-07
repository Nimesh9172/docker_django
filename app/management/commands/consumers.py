from django.core.management.base import BaseCommand
from kafka import KafkaConsumer
import json
from app.models import RiderLocation
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from app.serializers import RiderLocationSerializer


class Command(BaseCommand):
    help = "Consume Kafka topic and insert into DB + broadcast via WebSocket"

    def handle(self, *args, **kwargs):
        print("🚀 Starting Kafka consumer...")

        consumer = KafkaConsumer(
            "rider_locations",
            bootstrap_servers=[settings.KAFKA_BROKER_URL],
            group_id="rider_locations_consumer",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )
        print("✅ Kafka consumer started (listening on 'rider_locations')")

        try:
            for message in consumer:
                print(f"📩 Received: {message.value}")
                data = message.value

                try:
                    # Insert into DB
                    obj = RiderLocation.objects.create(**data)
                    serializer = RiderLocationSerializer(obj)
                    print(f"✅ Inserted into DB: {serializer.data}")

                    # Broadcast to WebSocket group
                    channel_layer = get_channel_layer()
                    if channel_layer:
                        async_to_sync(channel_layer.group_send)(
                            "rider_updates",
                            {
                                "type": "rider_update",
                                "data": serializer.data,
                            },
                        )
                        print("📡 Broadcasted to WebSocket clients")

                except Exception as e:
                    print(f"❌ Error processing message: {e}")

        except KeyboardInterrupt:
            print("🛑 Kafka consumer stopped by user")
        finally:
            consumer.close()
            print("🛑 Kafka consumer closed")