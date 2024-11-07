# notifications/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            await self.channel_layer.group_add(
                f"user_notifications_{user.id}",
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        user = self.scope["user"]
        await self.channel_layer.group_discard(
            f"user_notifications_{user.id}",
            self.channel_name
        )

    async def notification_event(self, event):
        await self.send(text_data=json.dumps(event['data']))

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=self.scope["user"]
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'mark_read':
            success = await self.mark_notification_read(data.get('notification_id'))
            await self.send(json.dumps({
                'type': 'mark_read_response',
                'success': success,
                'notification_id': data.get('notification_id')
            }))