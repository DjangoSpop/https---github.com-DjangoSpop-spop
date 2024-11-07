# officers/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class Officer(models.Model):
    STATUS_CHOICES = [
        ('available', 'متاح'),
        ('on_mission', 'في مهمة'),
        ('on_leave', 'إجازة'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='officer_profile'
    )
    name = models.CharField(max_length=255)
    rank = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )
    phone_number = models.CharField(max_length=15)
    specializations = models.JSONField(default=list)
    last_active = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.rank} {self.name}"

    def save(self, *args, **kwargs):
        self.last_active = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_available(self):
        return self.status == 'available'

    @property
    def active_tasks(self):
        return self.assigned_tasks.exclude(status__in=['completed', 'cancelled'])

    @property
    def completed_tasks(self):
        return self.assigned_tasks.filter(status='completed')