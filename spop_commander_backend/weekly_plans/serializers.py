# weekly_plans/serializers.py
from rest_framework import serializers
from .models import WeeklyPlan
import hashlib

class WeeklyPlanSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = WeeklyPlan
        fields = ['id', 'photo', 'photo_url', 'week_start_date', 'week_end_date',
                 'plan_type', 'description', 'created_at', 'created_by',
                 'file_size', 'file_hash']
        read_only_fields = ['created_at', 'created_by', 'file_hash']

    def get_photo_url(self, obj):
        return obj.photo.url if obj.photo else None

    def get_file_size(self, obj):
        return obj.photo.size if obj.photo else None

    def validate(self, data):
        if data['week_end_date'] < data['week_start_date']:
            raise serializers.ValidationError("End date must be after start date")
        return data

    def create(self, validated_data):
        # Calculate file hash for integrity
        if 'photo' in validated_data:
            hasher = hashlib.sha256()
            for chunk in validated_data['photo'].chunks():
                hasher.update(chunk)
            validated_data['file_hash'] = hasher.hexdigest()
        return super().create(validated_data)