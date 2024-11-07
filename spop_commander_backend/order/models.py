from django.db import models
from core.models import BaseModel
from django.conf import settings
from officers.models import Officer


class Order(BaseModel):
    PRIORITY_CHOICES = [
        ('normal', 'عادي'),
        ('high', 'عالي'),
        ('urgent', 'عاجل'),
    ]

    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('in_progress', 'جاري التنفيذ'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_orders'
    )
    assigned_to = models.ForeignKey(
        Officer,
        on_delete=models.CASCADE,
        related_name='assigned_orders'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    due_date = models.DateTimeField()
    is_urgent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class OrderAcknowledgment(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='acknowledgments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    acknowledged_at = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True)
