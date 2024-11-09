from rest_framework import serializers

from circular.models import Circular, CircularAcknowledgment, CircularAttachment


class CircularAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CircularAttachment
        fields = ['id', 'file_name', 'file_type', 'file_size', 'file_path', 'server_url']

class CircularAcknowledgmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CircularAcknowledgment
        fields = ['officer', 'timestamp', 'device_info', 'ip_address', 'location']

class CircularSerializer(serializers.ModelSerializer):
    attachments = CircularAttachmentSerializer(many=True, read_only=True)
    acknowledgments = CircularAcknowledgmentSerializer(many=True, read_only=True)
    read_percentage = serializers.FloatField(read_only=True)
    read_count = serializers.IntegerField(read_only=True)
    total_recipients = serializers.IntegerField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Circular
        fields = [
            'id', 'title', 'content', 'created_by', 'created_at',
            'classification', 'expiry_date', 'target_officers',
            'is_confidential', 'is_deleted', 'circular_number',
            'metadata', 'attachments', 'acknowledgments',
            'read_percentage', 'read_count', 'total_recipients',
            'is_expired'
        ]