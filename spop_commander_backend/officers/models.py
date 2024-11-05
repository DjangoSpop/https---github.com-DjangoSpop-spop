from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image
from django.utils import timezone


# Officer model
class Officer(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)
    rank = models.CharField(max_length=100)
    photo = models.URLField(blank=True, null=True)
    specializations = models.JSONField()  # To store list of specializations
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    completed_tasks_count = models.IntegerField(default=0)
    pending_tasks_count = models.IntegerField(default=0)
    last_active = models.DateTimeField()

    def __str__(self):
        return self.name