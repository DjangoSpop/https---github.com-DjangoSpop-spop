

from django.contrib import admin
from .models import (
    DashboardMetric,
    PerformanceSnapshot,
    Activity,
    DashboardCache,
    NotificationPreference
)

@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = ('metric_type', 'metric_value', 'category', 'timestamp')
    list_filter = ('metric_type', 'category', 'timestamp')
    search_fields = ('metric_type', 'metric_label')

@admin.register(PerformanceSnapshot)
class PerformanceSnapshotAdmin(admin.ModelAdmin):
    list_display = ('date', 'completion_rate', 'total_tasks', 'total_officers')
    list_filter = ('date',)
    date_hierarchy = 'date'

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('activity_type', 'title', 'actor', 'timestamp')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('title', 'description')
    raw_id_fields = ('actor', 'related_officer')

@admin.register(DashboardCache)
class DashboardCacheAdmin(admin.ModelAdmin):
    list_display = ('cache_key', 'expires_at', 'updated_at')
    list_filter = ('expires_at', 'updated_at')
    search_fields = ('cache_key',)

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_notifications', 'push_notifications')
    list_filter = ('email_notifications', 'push_notifications')
    raw_id_fields = ('user',)