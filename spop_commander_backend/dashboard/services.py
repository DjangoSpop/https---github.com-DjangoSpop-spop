from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_dashboard_update(update_type, data, user_id=None):
    """
    Send updates to connected WebSocket clients
    """
    channel_layer = get_channel_layer()

    if user_id:
        # Send to specific user
        async_to_sync(channel_layer.group_send)(
            f"dashboard_user_{user_id}",
            {
                "type": "dashboard_update",
                "data": {
                    "type": update_type,
                    "data": data
                }
            }
        )
    else:
        # Broadcast to all users
        async_to_sync(channel_layer.group_send)(
            "dashboard_updates",
            {
                "type": "dashboard_update",
                "data": {
                    "type": update_type,
                    "data": data
                }
            }
        )