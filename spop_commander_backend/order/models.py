from django.db import models
from django.utils import timezone


# Create your models here.
class Order(models.Model):
    class OrderPriority(models.IntegerChoices):
        LOW = 0, 'Low'
        MEDIUM = 1, 'Medium'
        HIGH = 2, 'High'

    class OrderStatus(models.IntegerChoices):
        PENDING = 0, 'Pending'
        IN_PROGRESS = 1, 'In Progress'
        COMPLETED = 2, 'Completed'
        CANCELLED = 3, 'Cancelled'

    id = models.CharField(primary_key=True, max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.IntegerField(choices=OrderPriority.choices, default=OrderPriority.LOW)
    status = models.IntegerField(choices=OrderStatus.choices, default=OrderStatus.PENDING)
    assigned_to = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    comments = models.JSONField(default=list)  # List of comments as JSON
    metadata = models.JSONField(blank=True, null=True)  # Optional metadata

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"