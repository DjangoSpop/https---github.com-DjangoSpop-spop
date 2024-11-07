# authentication/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    RANK_CHOICES = [
        ('commander', 'Commander'),
        ('lieutenant', 'Lieutenant'),
        ('captain', 'Captain'),
        ('major', 'Major'),
        ('colonel', 'Colonel'),

    ]

    phone_number = models.CharField(max_length=15, blank=True)
    rank = models.CharField(
        max_length=50,
        choices=RANK_CHOICES,
        blank=True
    )
    military_number = models.CharField(max_length=15, blank=True)
    national_id = models.CharField(max_length=15, blank=True)
    is_commander = models.BooleanField(default=False)

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.rank} {self.username}" if self.rank else self.username

    def get_full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username

    @property
    def is_staff_member(self):
        return self.is_staff or self.is_commander
