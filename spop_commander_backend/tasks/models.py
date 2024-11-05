from django.db import models

# Create your models here.
from django.db import models
from core.models import BaseModel
from authentication.models import User


class Task(BaseModel):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name='assigned_tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='created_tasks')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES,
                                default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default='pending')
    due_date = models.DateTimeField()
    completion_rate = models.FloatField(default=0.0)


class TaskUpdate(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE,
                             related_name='updates')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    update_type = models.CharField(max_length=20)
    description = models.TextField()
    data = models.JSONField(null=True, blank=True)
