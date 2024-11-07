from rest_framework import serializers
from .models import Notification, NotificationPreference

class NotificationSerializer(serializers.ModelSerializer):
    is_read = serializers.BooleanField(read_only=True)
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id',
            'type',
            'title',
            'body',
            'created_at',
            'is_read',
            'action_id',
            'action_type',
            'metadata',
            'priority',
            'time_ago',
        ]
        read_only_fields = ['created_at', 'is_read']

    def get_time_ago(self, obj):
        from django.utils import timezone
        from django.utils.timesince import timesince
        now = timezone.now()
        return timesince(obj.created_at, now)

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'email_enabled',
            'push_enabled',
            'quiet_hours_start',
            'quiet_hours_end',
            'disabled_types',
        ]
