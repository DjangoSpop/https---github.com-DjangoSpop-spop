from rest_framework import serializers
from .models import Task, TaskUpdate

class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskUpdate
        fields = ['id', 'update_type', 'description', 'created_at', 'data']

class TaskSerializer(serializers.ModelSerializer):
    updates = TaskUpdateSerializer(many=True, read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name',
                                          read_only=True)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']