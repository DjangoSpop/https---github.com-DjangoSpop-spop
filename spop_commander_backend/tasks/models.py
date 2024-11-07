from django.db import models
from core.models import BaseModel
from django.conf import settings
from officers.models import Officer


class Task(BaseModel):
    PRIORITY_CHOICES = [
        ('low', 'منخفض'),
        ('medium', 'متوسط'),
        ('high', 'عالي'),
        ('urgent', 'عاجل'),
    ]

    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(
        Officer,
        on_delete=models.CASCADE,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    start_date = models.DateTimeField()
    due_date = models.DateTimeField()
    completion_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class TaskUpdate(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='updates')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    update_type = models.CharField(max_length=20)
    description = models.TextField()
    data = models.JSONField(null=True, blank=True)
