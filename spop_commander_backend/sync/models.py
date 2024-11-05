from django.db import models

# Create your models here.
from django.db import models
from spop_commander_backend.core.models import BaseModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class SyncStatus(BaseModel):
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField()
    last_sync = models.DateTimeField()
    is_synced = models.BooleanField(default=False)
    sync_attempts = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        unique_together = ['entity_type', 'entity_id']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
        ]


class SyncQueue(BaseModel):
    SYNC_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')

    sync_type = models.CharField(max_length=10, choices=SYNC_TYPES)
    data = models.JSONField()
    priority = models.IntegerField(default=0)
    attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(null=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['priority', 'created_at']
