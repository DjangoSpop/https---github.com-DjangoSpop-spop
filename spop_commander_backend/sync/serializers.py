from rest_framework import serializers
from .models import SyncStatus, SyncQueue

class SyncStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncStatus
        fields = '__all__'

class SyncQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncQueue
        fields = '__all__'
