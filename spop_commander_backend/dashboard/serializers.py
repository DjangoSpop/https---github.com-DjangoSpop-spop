# dashboard/serializers.py

from rest_framework import serializers

class OfficerStatsSerializer(serializers.Serializer):
    total_officers = serializers.IntegerField()
    available_officers = serializers.IntegerField()
    on_mission_officers = serializers.IntegerField()
    on_leave_officers = serializers.IntegerField()

class TaskStatsSerializer(serializers.Serializer):
    total_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    in_progress_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()

class OrderStatsSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    urgent_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    recent_orders = serializers.IntegerField()

class ActivitySerializer(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.CharField()
    title = serializers.CharField()
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    officer = serializers.CharField()

class PerformanceMetricsSerializer(serializers.Serializer):
    task_metrics = serializers.DictField()
    officer_metrics = serializers.DictField()

class DashboardSummarySerializer(serializers.Serializer):
    officers = OfficerStatsSerializer()
    tasks = TaskStatsSerializer()
    orders = OrderStatsSerializer()
    recent_activities = ActivitySerializer(many=True)
    performance_metrics = PerformanceMetricsSerializer()
    last_updated = serializers.DateTimeField()