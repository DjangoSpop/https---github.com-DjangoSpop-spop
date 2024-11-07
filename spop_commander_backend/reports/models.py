from django.db import models
from django.utils import timezone
from authentication.models import User


# Create your models here.
class ReportStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    NEEDS_REVISION = 'needs_revision', 'Needs Revision'
    ARCHIVED = 'archived', 'Archived'

class Reports(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='reports')
    officer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports")
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="reviewed_reports")
    reviewed_at = models.DateTimeField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    awards_points = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.title

class ReportAttachment(models.Model):
    report = models.ForeignKey(Reports, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="report_attachments")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ReportStatistics(models.Model):
    officer = models.ForeignKey(User, on_delete=models.CASCADE)
    total_reports = models.IntegerField()
    pending_reports = models.IntegerField()
    approved_reports = models.IntegerField()
    rejected_reports = models.IntegerField()
    average_response_time = models.DurationField(blank=True, null=True)



