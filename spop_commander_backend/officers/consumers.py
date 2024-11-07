import json
from channels.generic.websocket import AsyncWebsocketConsumer


class OfficerUpdatesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not await self.authenticate_user():
            await self.close()
            return
        self.officer_id = self.scope['url_route']['kwargs']['officer_id']
        self.room_group_name = f'officer_{self.officer_id}_updates'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Handle received message types (e.g., task_update, status_change)
        message_type = data.get("type")
        if message_type == "task_update":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "task_update",
                    "data": data
                }
            )
        elif message_type == "status_change":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "status_change",
                    "data": data
                }
            )

    async def task_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    async def status_change(self, event):
        await self.send(text_data=json.dumps(event["data"]))
