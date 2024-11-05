from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_commander = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True)
    rank = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'auth_user'
