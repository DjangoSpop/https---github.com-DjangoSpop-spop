# circulars/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

class CircularClassification(models.TextChoices):
    NORMAL = 'NORMAL', 'Normal'
    CONFIDENTIAL = 'CONFIDENTIAL', 'Confidential'
    TOP_SECRET = 'TOP_SECRET', 'Top Secret'
    RESTRICTED = 'RESTRICTED', 'Restricted'

class Circular(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='created_circulars')
    created_at = models.DateTimeField(auto_now_add=True)
    classification = models.CharField(
        max_length=20,
        choices=CircularClassification.choices,
        default=CircularClassification.NORMAL
    )
    expiry_date = models.DateTimeField()
    target_officers = models.ManyToManyField(get_user_model(), related_name='targeted_circulars')
    is_confidential = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    circular_number = models.CharField(max_length=50, unique=True)
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_expired(self):
        return timezone.now() > self.expiry_date

    @property
    def read_count(self):
        return self.acknowledgments.count()

    @property
    def total_recipients(self):
        return self.target_officers.count()

    @property
    def read_percentage(self):
        if self.total_recipients > 0:
            return (self.read_count / self.total_recipients) * 100
        return 0

    def has_officer_read(self, officer_id):
        return self.acknowledgments.filter(officer_id=officer_id).exists()

    def can_officer_access(self, officer_id):
        return (
            self.target_officers.filter(id=officer_id).exists() 
            and not self.is_deleted 
            and not self.is_expired
        )

class CircularAcknowledgment(models.Model):
    circular = models.ForeignKey(Circular, on_delete=models.CASCADE, related_name='acknowledgments')
    officer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='circular_acknowledgments')
    timestamp = models.DateTimeField(auto_now_add=True)
    device_info = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    location = models.CharField(max_length=255)

    class Meta:
        unique_together = ['circular', 'officer']

class CircularAttachment(models.Model):
    id = models.UUIDField(primary_key=True)
    circular = models.ForeignKey(Circular, on_delete=models.CASCADE, related_name='attachments')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    file_size = models.IntegerField()
    file_path = models.FileField(upload_to='circular_attachments/')
    server_url = models.URLField(null=True, blank=True)