# dashboard/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Activity, DashboardMetric, PerformanceSnapshot
from officers.models import Officer
from tasks.models import Task
from order.models import Order

@receiver(post_save, sender=Task)
def track_task_updates(sender, instance, created, **kwargs):
    """Track task updates for dashboard"""
    if created:
        activity_type = 'task'
        title = f'New Task Created: {instance.title}'
    else:
        activity_type = 'task'
        title = f'Task Updated: {instance.title}'

    Activity.objects.create(
        activity_type=activity_type,
        title=title,
        description=instance.description,
        actor=instance.created_by,
        related_officer=instance.assigned_to,
        status=instance.status,
        metadata={
            'task_id': instance.id,
            'priority': instance.priority,
            'due_date': instance.due_date.isoformat() if instance.due_date else None
        }
    )

@receiver(post_save, sender=Officer)
def track_officer_updates(sender, instance, created, **kwargs):
    """Track officer status changes"""
    if not created:
        Activity.objects.create(
            activity_type='officer',
            title=f'Officer Status Update: {instance.name}',
            description=f'Status changed to {instance.status}',
            related_officer=instance,
            status=instance.status
        )

@receiver(post_save, sender=Order)
def track_order_updates(sender, instance, created, **kwargs):
    """Track order updates for dashboard"""
    if created:
        title = f'New Order Created: {instance.title}'
    else:
        title = f'Order Updated: {instance.title}'

    Activity.objects.create(
        activity_type='order',
        title=title,
        description=instance.description,
        actor=instance.created_by,
        related_officer=instance.assigned_to,
        status=instance.status,
        metadata={
            'order_id': instance.id,
            'priority': instance.priority,
        }
    )