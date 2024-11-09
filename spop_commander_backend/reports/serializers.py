# reports/serializers.py
from rest_framework import serializers
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Reports, ReportAttachment, ReportStatistics, ReportStatus
from authentication.serializers import UserSerializer


class ReportAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = ReportAttachment
        fields = ['id', 'report', 'file', 'file_url', 'file_name', 'file_size', 'uploaded_at']
        read_only_fields = ['uploaded_at']

    def get_file_url(self, obj):
        try:
            return obj.file.url
        except:
            return None

    def get_file_name(self, obj):
        return obj.file.name.split('/')[-1] if obj.file else None

    def get_file_size(self, obj):
        try:
            return obj.file.size
        except:
            return None

    def validate_file(self, value):
        # Add file size validation (e.g., 10MB limit)
        if value.size > 10 * 1024 * 1024:
            raise ValidationError('File size cannot exceed 10MB')
        return value


class ReportStatisticsSerializer(serializers.ModelSerializer):
    officer_details = UserSerializer(source='officer', read_only=True)
    efficiency_rate = serializers.SerializerMethodField()

    class Meta:
        model = ReportStatistics
        fields = [
            'id', 'officer', 'officer_details',
            'total_reports', 'pending_reports',
            'approved_reports', 'rejected_reports',
            'average_response_time', 'efficiency_rate'
        ]
        read_only_fields = ['officer']

    def get_efficiency_rate(self, obj):
        if obj.total_reports > 0:
            return (obj.approved_reports / obj.total_reports) * 100
        return 0

    def validate(self, data):
        # Ensure report counts add up correctly
        total = data.get('total_reports', 0)
        pending = data.get('pending_reports', 0)
        approved = data.get('approved_reports', 0)
        rejected = data.get('rejected_reports', 0)

        if total != (pending + approved + rejected):
            raise serializers.ValidationError(
                "Total reports must equal sum of pending, approved, and rejected reports"
            )
        return data


class ReportSerializer(serializers.ModelSerializer):
    attachments = ReportAttachmentSerializer(many=True, read_only=True)
    officer_details = UserSerializer(source='officer', read_only=True)
    reviewer_details = UserSerializer(source='reviewed_by', read_only=True)
    status = serializers.ChoiceField(choices=ReportStatus.choices, required=False)
    time_since_submission = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_review = serializers.SerializerMethodField()

    class Meta:
        model = Reports
        fields = [
            'id', 'title', 'description', 'image',
            'officer', 'officer_details',
            'reviewed_by', 'reviewer_details',
            'reviewed_at', 'feedback',
            'awards_points', 'submitted_at',
            'attachments', 'status',
            'time_since_submission',
            'can_edit', 'can_review'
        ]
        read_only_fields = [
            'officer', 'reviewed_by', 'reviewed_at',
            'awards_points', 'submitted_at'
        ]

    def get_time_since_submission(self, obj):
        if obj.submitted_at:
            time_diff = timezone.now() - obj.submitted_at
            days = time_diff.days
            hours = time_diff.seconds // 3600
            minutes = (time_diff.seconds % 3600) // 60

            if days > 0:
                return f"{days} days ago"
            elif hours > 0:
                return f"{hours} hours ago"
            else:
                return f"{minutes} minutes ago"
        return None

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return False

        # Officer can edit if report is pending or needs revision
        return (
                request.user == obj.officer and
                obj.status in [ReportStatus.PENDING, ReportStatus.NEEDS_REVISION]
        )

    def get_can_review(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return False

        # Only supervisors can review, and not their own reports
        return (
                request.user.is_supervisor and
                request.user != obj.officer and
                obj.status == ReportStatus.PENDING
        )

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError(
                "Title must be at least 5 characters long"
            )
        return value

    def validate_description(self, value):
        if len(value) < 20:
            raise serializers.ValidationError(
                "Description must be at least 20 characters long"
            )
        return value

    def validate(self, data):
        # Add any cross-field validation here
        if self.instance and self.instance.status == ReportStatus.ARCHIVED:
            raise serializers.ValidationError(
                "Archived reports cannot be modified"
            )
        return data


class ReportReviewSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=ReportStatus.choices)
    feedback = serializers.CharField(required=False, allow_blank=True)
    awards_points = serializers.IntegerField(required=False, min_value=0, max_value=100)

    def validate_decision(self, value):
        if value not in [ReportStatus.APPROVED, ReportStatus.REJECTED, ReportStatus.NEEDS_REVISION]:
            raise serializers.ValidationError(
                "Invalid review decision"
            )
        return value

    def validate(self, data):
        if data.get('decision') == ReportStatus.REJECTED and not data.get('feedback'):
            raise serializers.ValidationError(
                "Feedback is required when rejecting a report"
            )
        return data


class ReportRevisionSerializer(serializers.Serializer):
    feedback = serializers.CharField(required=True)
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False
    )

    def validate_feedback(self, value):
        if len(value) < 10:
            raise serializers.ValidationError(
                "Revision feedback must be at least 10 characters long"
            )
        return value