from django.db import models

# Create your models here.
# weekly_plans/models.py
from django.db import models
from django.core.validators import FileExtensionValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from PIL import Image
import os

def validate_image_size(value):
    if value.size > 5 * 1024 * 1024:  # 5MB limit
        raise ValidationError('Image size must be less than 5MB')

def compress_image(image):
    img = Image.open(image)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    # Set max dimensions
    output_size = (1024, 1024)
    img.thumbnail(output_size)
    # Save with reduced quality
    img.save(image.path, quality=60, optimize=True)

class WeeklyPlan(models.Model):
    PLAN_TYPES = (
        ('officer', 'Officer'),
        ('sergeant', 'Sergeant'),
    )

    photo = models.ImageField(
        upload_to='weekly_plans/%Y/%m/',
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png']),
            validate_image_size
        ]
    )
    week_start_date = models.DateField()
    week_end_date = models.DateField()
    plan_type = models.CharField(max_length=10, choices=PLAN_TYPES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    file_hash = models.CharField(max_length=64, blank=True)  # For integrity check

    def save(self, *args, **kwargs):
        if not self.pk:  # New instance
            super().save(*args, **kwargs)
            compress_image(self.photo)
        else:
            super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ("can_view_all_plans", "Can view all weekly plans"),
            ("can_upload_plans", "Can upload weekly plans"),
        ]