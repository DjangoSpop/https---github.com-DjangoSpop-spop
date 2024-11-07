# officers/serializers.py
from rest_framework import serializers
from .models import Officer
from tasks.serializers import TaskSerializer
from tasks.models import Task

class OfficerSerializer(serializers.ModelSerializer):
    active_tasks_count = serializers.SerializerMethodField()
    completed_tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Officer
        fields = [
            'id', 'user', 'name', 'rank', 'status', 'phone_number',
            'specializations', 'active_tasks_count', 'completed_tasks_count',
            'last_active'
        ]
        read_only_fields = ['last_active']

    def get_active_tasks_count(self, obj):
        return Task.objects.filter(
            assigned_officer=obj,
            status__in=['pending', 'in_progress']
        ).count()

    def get_completed_tasks_count(self, obj):
        return Task.objects.filter(
            assigned_officer=obj,
            status='completed'
        ).count()

    def validate_phone_number(self, value):
        """Validate phone number format"""
        if not value.isdigit() or len(value) < 10:
            raise serializers.ValidationError(
                "رقم الهاتف غير صالح"
            )
        return value

class OfficerDetailSerializer(OfficerSerializer):
    active_tasks = serializers.SerializerMethodField()
    recent_tasks = serializers.SerializerMethodField()
    performance_metrics = serializers.SerializerMethodField()

    class Meta(OfficerSerializer.Meta):
        fields = OfficerSerializer.Meta.fields + [
            'active_tasks', 'recent_tasks', 'performance_metrics'
        ]

    def get_active_tasks(self, obj):
        tasks = Task.objects.filter(
            assigned_officer=obj,
            status__in=['pending', 'in_progress']
        ).order_by('-created_at')[:5]
        return TaskSerializer(tasks, many=True).data

    def get_recent_tasks(self, obj):
        tasks = Task.objects.filter(
            assigned_officer=obj,
            status='completed'
        ).order_by('-completed_at')[:5]
        return TaskSerializer(tasks, many=True).data

    def get_performance_metrics(self, obj):
        total_tasks = Task.objects.filter(assigned_officer=obj).count()
        completed_tasks = Task.objects.filter(
            assigned_officer=obj,
            status='completed'
        ).count()

        return {
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks
        }