import json
from channels.generic.websocket import AsyncWebsocketConsumer

class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({"message": "WebSocket connected!"}))

    async def receive(self, text_data):
        await self.send(text_data=json.dumps({
            "echo": text_data
        }))

    async def disconnect(self, close_code):
        pass


class RiderLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("rider_updates", self.channel_name)
        await self.accept()
        await self.send(json.dumps({"message": "Connected to rider updates"}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("rider_updates", self.channel_name)

    async def rider_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("rider_updates", self.channel_name)
