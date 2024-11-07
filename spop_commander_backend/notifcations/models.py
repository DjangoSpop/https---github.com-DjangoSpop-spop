from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class NotificationType(models.TextChoices):
    TASK = 'task', 'Task'
    ORDER = 'order', 'Order'
    ALERT = 'alert', 'Alert'
    SYSTEM = 'system', 'System'
    URGENT = 'urgent', 'Urgent'


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    action_id = models.CharField(max_length=255, null=True, blank=True)
    action_type = models.CharField(max_length=50, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    priority = models.IntegerField(default=0)

    # Generic relation to related object
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.CharField(max_length=255, null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['type', '-created_at']),
            models.Index(fields=['priority', '-created_at']),
        ]

    @property
    def is_read(self):
        return self.read_at is not None

    def mark_as_read(self):
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=['read_at'])

    def mark_as_unread(self):
        if self.read_at:
            self.read_at = None
            self.save(update_fields=['read_at'])


class NotificationPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    disabled_types = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name_plural = 'Notification preferences'