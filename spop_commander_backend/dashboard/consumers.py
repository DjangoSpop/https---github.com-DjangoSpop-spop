import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.request.Request import user
from rest_framework.response import Response

from authentication.serializers import UserDetailSerializer
from officers.models import Officer
from order.models import Order
from tasks.models import Task


class DashboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time dashboard updates
    """

    async def connect(self):
        """
        Called when a client attempts to establish a WebSocket connection
        """
        try:
            # Authenticate the connection
            if not await self.authenticate_user():
                await self.close(code=4001)
                return

            # Add user to their specific dashboard group
            user_group = f"dashboard_user_{self.user.id}"
            await self.channel_layer.group_add(user_group, self.channel_name)

            # Add to general dashboard updates group
            await self.channel_layer.group_add("dashboard_updates", self.channel_name)

            # Accept the connection
            await self.accept()

            # Send initial data
            await self.send_initial_data()

        except Exception as e:
            print(f"Connection error: {e}")
            await self.close(code=4002)

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason
        """
        try:
            # Remove from groups
            user_group = f"dashboard_user_{self.user.id}"
            await self.channel_layer.group_discard(user_group, self.channel_name)
            await self.channel_layer.group_discard("dashboard_updates", self.channel_name)
        except Exception as e:
            print(f"Disconnect error: {e}")

    async def receive(self, text_data):
        """
        Called when data is received from the client
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            # Handle different types of messages
            handlers = {
                'request_stats_update': self.handle_stats_request,
                'request_officer_update': self.handle_officer_request,
                'request_tasks_update': self.handle_tasks_request,
                'request_orders_update': self.handle_orders_request,
                'ping': self.handle_ping,
            }

            handler = handlers.get(message_type)
            if handler:
                await handler(data)
            else:
                await self.send_error('Unsupported message type')

        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            await self.send_error(f'Error processing message: {str(e)}')

    @database_sync_to_async
    def authenticate_user(self):
        """
        Authenticate the WebSocket connection using token
        """
        try:
            token = next((p for p in self.scope['subprotocols']
                          if p != 'bearer-token'), None)

            if not token:
                return False

            # Your token validation logic here
            self.user = Response({'token': token, 'user':UserDetailSerializer(user).data})  # Get user from token
            return True if self.user else False

        except Exception:
            return False

    async def send_initial_data(self):
        """
        Send initial dashboard data when connection is established
        """
        try:
            stats = await self.get_dashboard_stats()
            await self.send(text_data=json.dumps({
                'type': 'initial_data',
                'data': stats
            }))
        except Exception as e:
            print(f"Error sending initial data: {e}")

    @database_sync_to_async
    def get_dashboard_stats(self):
        """
        Get current dashboard statistics
        """
        return {
            'total_officers': Officer.objects.count(),
            'active_officers': Officer.objects.filter(status='active').count(),
            'pending_tasks': Task.objects.filter(status='pending').count(),
            'urgent_orders': Order.objects.filter(priority='urgent').count(),
        }

    async def handle_stats_request(self, data):
        """
        Handle request for updated statistics
        """
        stats = await self.get_dashboard_stats()
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'data': stats
        }))

    async def handle_ping(self, data):
        """
        Handle ping messages to keep connection alive
        """
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': data.get('timestamp')
        }))

    async def dashboard_update(self, event):
        """
        Handle dashboard updates from other parts of the application
        """
        await self.send(text_data=json.dumps(event['data']))

    async def send_error(self, message):
        """
        Send error message to client
        """
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
