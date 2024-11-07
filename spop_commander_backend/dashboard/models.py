# dashboard/models.py

from django.db import models
from django.utils import timezone
from django.conf import settings


class DashboardMetric(models.Model):
    """Store key dashboard metrics and their history"""
    metric_type = models.CharField(max_length=50)
    metric_value = models.FloatField()
    metric_label = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=['metric_type', 'timestamp']),
            models.Index(fields=['category', 'timestamp']),
        ]
        ordering = ['-timestamp']


class PerformanceSnapshot(models.Model):
    """Daily performance metrics snapshot"""
    date = models.DateField(unique=True)
    total_officers = models.IntegerField(default=0)
    available_officers = models.IntegerField(default=0)
    on_mission_officers = models.IntegerField(default=0)
    on_leave_officers = models.IntegerField(default=0)
    total_tasks = models.IntegerField(default=0)
    pending_tasks = models.IntegerField(default=0)
    in_progress_tasks = models.IntegerField(default=0)
    completed_tasks = models.IntegerField(default=0)
    overdue_tasks = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    avg_response_time = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['date'])]
        ordering = ['-date']


class Activity(models.Model):
    """Track all dashboard activities"""
    ACTIVITY_TYPES = (
        ('task', 'Task'),
        ('order', 'Order'),
        ('officer', 'Officer'),
        ('system', 'System'),
    )

    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='dashboard_activities'
    )
    related_officer = models.ForeignKey(
        'officers.Officer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities'
    )
    status = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['activity_type', 'timestamp']),
            models.Index(fields=['actor', 'timestamp']),
        ]
        ordering = ['-timestamp']


class DashboardCache(models.Model):
    """Cache dashboard data to improve performance"""
    cache_key = models.CharField(max_length=100, unique=True)
    cache_data = models.JSONField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['expires_at']),
        ]


class NotificationPreference(models.Model):
    """User preferences for dashboard notifications"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboard_preferences'
    )
    notify_on_metric_change = models.BooleanField(default=True)
    notify_on_task_update = models.BooleanField(default=True)
    notify_on_officer_status = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    notification_threshold = models.FloatField(default=10.0)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['user'])]